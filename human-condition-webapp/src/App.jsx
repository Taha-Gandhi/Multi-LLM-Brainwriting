import { useEffect, useMemo, useState } from "react";
import {
  MessageCircle,
  Send,
  Lightbulb,
  Users,
  Vote,
  Download,
  EyeOff,
  Plus,
  CheckCircle2,
} from "lucide-react";
import "./index.css";

import {
  collection,
  addDoc,
  onSnapshot,
  orderBy,
  query,
  serverTimestamp,
  updateDoc,
  doc,
  increment,
  setDoc,
  getDoc,
  runTransaction,
  deleteDoc,
  deleteField,
} from "firebase/firestore";

import { db } from "./firebase";

const initialIdeas = [
  {
    id: "idea-a",
    title: "Campus Food Loop",
    body: "A simple campus system where students can claim surplus cafeteria meals through time-limited anonymous pickup slots.",
    createdAt: "09:12",
    votes: 3,
    comments: [
      {
        id: 1,
        author: "Anon 2",
        text: "Strong idea, but food safety rules need to be clear.",
        time: "09:18",
      },
      {
        id: 2,
        author: "Anon 5",
        text: "Maybe add pickup windows so food does not sit out too long.",
        time: "09:22",
      },
    ],
  },
  {
    id: "idea-b",
    title: "Smart Portion Reminder",
    body: "Students receive subtle reminders and recommendations based on common over-ordering patterns at campus food stalls.",
    createdAt: "09:15",
    votes: 2,
    comments: [
      {
        id: 1,
        author: "Anon 1",
        text: "Useful, but it may feel preachy if not designed carefully.",
        time: "09:20",
      },
    ],
  },
];

const initialChat = [
  {
    id: 1,
    author: "Anon 4",
    text: "I think the final idea should not require students to download another app.",
    time: "09:25",
  },
  {
    id: 2,
    author: "Anon 2",
    text: "Agree. Maybe WhatsApp or Telegram alerts are easier for the pilot.",
    time: "09:27",
  },
];

function timeNow() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function anonymousName() {
  return `Anon ${Math.floor(Math.random() * 9) + 1}`;
}

function getOrCreateParticipantId(sessionId) {
  const storageKey = `participant_id_${sessionId}`;
  const existingId = localStorage.getItem(storageKey);

  if (existingId) {
    return existingId;
  }

  const newId = `participant_${Date.now()}_${Math.random()
    .toString(36)
    .slice(2, 10)}`;

  localStorage.setItem(storageKey, newId);

  return newId;
}

function App() {
  const [ideas, setIdeas] = useState([]);
  const [chat, setChat] = useState([]);

  const [ideaTitle, setIdeaTitle] = useState("");
  const [ideaBody, setIdeaBody] = useState("");

  const [activeIdeaId, setActiveIdeaId] = useState("");
  const [commentDrafts, setCommentDrafts] = useState({});
  const [chatDraft, setChatDraft] = useState("");
  const [votedIdeas, setVotedIdeas] = useState({});
  const [participantVote, setParticipantVote] = useState("");
  const [finalTitle, setFinalTitle] = useState("");
  const [finalDescription, setFinalDescription] = useState("");

  const [participantName, setParticipantName] = useState("");
  const [studentId, setStudentId] = useState("");
  const [accessCode, setAccessCode] = useState("");
  const [accessStatus, setAccessStatus] = useState("not_requested");
  const [approvedParticipantId, setApprovedParticipantId] = useState("");
  const [accessError, setAccessError] = useState("");
  const sessionId = new URLSearchParams(window.location.search).get("session") || "default-session";
  const browserParticipantId = getOrCreateParticipantId(sessionId);
  const participantId = approvedParticipantId || browserParticipantId;
  const ideasCollectionRef = collection(db, "sessions", sessionId, "ideas");
  const chatCollectionRef = collection(db, "sessions", sessionId, "generalChat");
  const finalIdeaRef = doc(db, "sessions", sessionId, "sessionData", "finalIdea");
  
  const condition =
    new URLSearchParams(window.location.search).get("condition") || "1a";

    const participantRef = approvedParticipantId
    ? doc(db, "sessions", sessionId, "participants", approvedParticipantId)
    : null;

  const sessionAccessCodes = {
    pilot: "PILOT1A",
    "test-vote": "TEST1A",
    "group-1a-a": "GROUPA1A",
    "group-1a-b": "GROUPB1A",
    "group-1a-c": "GROUPC1A",
    "group-1b-a": "GROUPA1B",
    "group-1b-b": "GROUPB1B",
    "group-1b-c": "GROUPC1B",
    "default-session": "BRAINWRITE1A",
  };

const requiredAccessCode = sessionAccessCodes[sessionId];
const isAnonymousCondition = condition === "1a";
const conditionLabel = isAnonymousCondition
  ? "1a Anonymous Human Convergence"
  : "1b Open Human Convergence";

  const sortedIdeas = useMemo(() => {
    return [...ideas].sort((a, b) => b.votes - a.votes);
  }, [ideas]);

  const activeIdea =
    ideas.find((idea) => idea.id === activeIdeaId) || ideas[0] || null;

  const activeIdeaIsOwn = activeIdea?.authorParticipantId === participantId;
  const activeIdeaIsVoted = participantVote === activeIdea?.id;
  const hasVotedAnotherIdea = participantVote && participantVote !== activeIdea?.id;

  const totalComments = ideas.reduce(
    (total, idea) => total + idea.comments.length,
    0
  );

  const totalVotes = ideas.reduce((total, idea) => total + idea.votes, 0);
  useEffect(() => {
    const savedStudentId = localStorage.getItem(`approved_student_${sessionId}`);
  
    if (!savedStudentId) {
      setAccessStatus("not_requested");
      return;
    }
  
    const savedParticipantRef = doc(
      db,
      "sessions",
      sessionId,
      "participants",
      savedStudentId
    );
  
    const unsubscribe = onSnapshot(savedParticipantRef, (snapshot) => {
      if (!snapshot.exists()) {
        localStorage.removeItem(`approved_student_${sessionId}`);
        setApprovedParticipantId("");
        setAccessStatus("not_requested");
        return;
      }
  
      const data = snapshot.data();
  
      if (data.approved === true) {
        setApprovedParticipantId(savedStudentId);
        setAccessStatus("approved");
        setParticipantName(data.name || "");
        setStudentId(data.studentId || "");
        setParticipantVote(data.votedIdeaId || "");
      } else {
        setAccessStatus("pending");
        setParticipantName(data.name || "");
        setStudentId(data.studentId || "");
        setParticipantVote(data.votedIdeaId || "");
      }
    });
  
    return () => unsubscribe();
  }, [sessionId]);
  
  useEffect(() => {
    const ideasQuery = query(
      ideasCollectionRef,
      orderBy("createdAtTimestamp", "desc")
    );
  
    const unsubscribe = onSnapshot(ideasQuery, (snapshot) => {
      const loadedIdeas = snapshot.docs.map((document) => {
        const data = document.data();
  
        return {
          id: document.id,
          title: data.title,
          body: data.body,
          createdAt: data.createdAt || "",
          votes: data.votes || 0,
          comments: data.comments || [],
          votedBy: data.votedBy || {},
          authorParticipantId: data.authorParticipantId || "",
          authorName: data.authorName || "",
          authorStudentId: data.authorStudentId || "",
          displayAuthor: data.displayAuthor || "Anonymous Participant",
          condition: data.condition || condition,
        };
      });
  
      setIdeas(loadedIdeas);
  
      if (loadedIdeas.length > 0 && !activeIdeaId) {
        setActiveIdeaId(loadedIdeas[0].id);
      }
    });
  
    return () => unsubscribe();
  }, [activeIdeaId]);

  useEffect(() => {
    const chatQuery = query(
      chatCollectionRef,
      orderBy("createdAtTimestamp", "asc")
    );
  
    const unsubscribe = onSnapshot(chatQuery, (snapshot) => {
      const loadedChat = snapshot.docs.map((document) => {
        const data = document.data();
  
        return {
          id: document.id,
          author: data.author || "Anonymous Participant",
          authorParticipantId: data.authorParticipantId || "",
          authorName: data.authorName || "",
          authorStudentId: data.authorStudentId || "",
          text: data.text,
          time: data.time || "",
          condition: data.condition || condition,
        };
      });
  
      setChat(loadedChat);
    });
  
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    async function loadFinalIdea() {
      const finalIdeaSnapshot = await getDoc(finalIdeaRef);
  
      if (finalIdeaSnapshot.exists()) {
        const data = finalIdeaSnapshot.data();
  
        setFinalTitle(data.title || "");
        setFinalDescription(data.description || "");
      }
    }
  
    loadFinalIdea();
  }, []);

  function getDisplayAuthor() {
    if (isAnonymousCondition) {
      return anonymousName();
    }
  
    return participantName || "Named Participant";
  }

  async function handleAccessSubmit(event) {
    event.preventDefault();
  
    const cleanedName = participantName.trim();
    const cleanedStudentId = studentId.trim().toUpperCase();
    const cleanedCode = accessCode.trim().toUpperCase();
  
    if (!cleanedName || !cleanedStudentId || !cleanedCode) {
      setAccessError("Please fill in your name, student ID, and password.");
      return;
    }
  
    if (!requiredAccessCode) {
      setAccessError("This session is not configured. Please check the session link.");
      return;
    }
  
    if (cleanedCode !== requiredAccessCode) {
      setAccessError("Invalid password for this session.");
      return;
    }
  
    const studentParticipantRef = doc(
      db,
      "sessions",
      sessionId,
      "participants",
      cleanedStudentId
    );
  
    const existingParticipant = await getDoc(studentParticipantRef);
  
    if (existingParticipant.exists()) {
      const data = existingParticipant.data();
  
      await setDoc(
        studentParticipantRef,
        {
          name: cleanedName,
          studentId: cleanedStudentId,
          sessionId,
          condition,
          lastLoginAt: timeNow(),
          lastLoginAtTimestamp: serverTimestamp(),
        },
        { merge: true }
      );
  
      setApprovedParticipantId(cleanedStudentId);
      localStorage.setItem(`approved_student_${sessionId}`, cleanedStudentId);
  
      setParticipantName(data.name || cleanedName);
      setStudentId(data.studentId || cleanedStudentId);
      setParticipantVote(data.votedIdeaId || "");
  
      if (data.approved === true) {
        setAccessStatus("approved");
      } else {
        setAccessStatus("pending");
      }
  
      setAccessError("");
      return;
    }
  
    await setDoc(
      studentParticipantRef,
      {
        participantId: cleanedStudentId,
        name: cleanedName,
        studentId: cleanedStudentId,
        sessionId,
        condition,
        approved: false,
        requestedAt: timeNow(),
        requestedAtTimestamp: serverTimestamp(),
        lastLoginAt: timeNow(),
        lastLoginAtTimestamp: serverTimestamp(),
      },
      { merge: true }
    );
  
    setApprovedParticipantId(cleanedStudentId);
    localStorage.setItem(`approved_student_${sessionId}`, cleanedStudentId);
  
    setAccessError("");
    setAccessStatus("pending");
  }

  async function deleteOwnIdea(ideaId) {
    const idea = ideas.find((item) => item.id === ideaId);
  
    if (!idea) return;
  
    if (idea.authorParticipantId !== participantId) {
      alert("You can only delete your own idea.");
      return;
    }
  
    const confirmDelete = window.confirm(
      "Are you sure you want to delete your idea? You will be able to submit a new one after deleting it."
    );
  
    if (!confirmDelete) return;
  
    const ideaRef = doc(db, "sessions", sessionId, "ideas", ideaId);
  
    await deleteDoc(ideaRef);
  
    if (activeIdeaId === ideaId) {
      setActiveIdeaId("");
    }
  
    setIdeaTitle("");
    setIdeaBody("");
  }

  async function submitIdea(event) {
    event.preventDefault();

    if (!ideaTitle.trim() || !ideaBody.trim()) return;
  
    const newIdea = {
      title: ideaTitle.trim(),
      body: ideaBody.trim(),
      createdAt: timeNow(),
      createdAtTimestamp: serverTimestamp(),
      votes: 0,
      comments: [],
      authorParticipantId: participantId,
      authorName: participantName,
      authorStudentId: studentId,
      displayAuthor: getDisplayAuthor(),
      condition,
    };
  
    const docRef = await addDoc(ideasCollectionRef, newIdea);
  
    setActiveIdeaId(docRef.id);
    setIdeaTitle("");
    setIdeaBody("");
  }

  async function submitComment(ideaId) {
    const text = commentDrafts[ideaId]?.trim();
  
    if (!text) return;
  
    const idea = ideas.find((item) => item.id === ideaId);
  
    if (!idea) return;
  
    const updatedComments = [
      ...idea.comments,
      {
        id: Date.now(),
        author: getDisplayAuthor(),
        authorParticipantId: participantId,
        authorName: participantName,
        authorStudentId: studentId,
        text,
        time: timeNow(),
        condition,
      },
    ];
  
    const ideaRef = doc(db, "sessions", sessionId, "ideas", ideaId);
  
    await updateDoc(ideaRef, {
      comments: updatedComments,
    });
  
    setCommentDrafts((prev) => ({
      ...prev,
      [ideaId]: "",
    }));
  }

  async function submitChat(event) {
    event.preventDefault();
  
    if (!chatDraft.trim()) return;
  
    await addDoc(chatCollectionRef, {
      author: getDisplayAuthor(),
      authorParticipantId: participantId,
      authorName: participantName,
      authorStudentId: studentId,
      text: chatDraft.trim(),
      time: timeNow(),
      createdAtTimestamp: serverTimestamp(),
      condition,
    });
  
    setChatDraft("");
  }

  async function voteIdea(ideaId) {
    const selectedIdea = ideas.find((idea) => idea.id === ideaId);
  
    if (!selectedIdea) return;
  
    if (selectedIdea.authorParticipantId === participantId) {
      alert("You cannot vote for your own idea.");
      return;
    }
  
    const selectedIdeaRef = doc(db, "sessions", sessionId, "ideas", ideaId);
  
    try {
      await runTransaction(db, async (transaction) => {
        if (!participantRef) {
          throw new Error("Participant record not ready.");
        }
        const participantSnapshot = await transaction.get(participantRef);
        const selectedIdeaSnapshot = await transaction.get(selectedIdeaRef);
  
        if (!selectedIdeaSnapshot.exists()) {
          throw new Error("Idea does not exist.");
        }
  
        const participantData = participantSnapshot.exists()
          ? participantSnapshot.data()
          : {};
  
        const previousVoteId = participantData.votedIdeaId || "";
  
        if (previousVoteId === ideaId) {
          transaction.update(selectedIdeaRef, {
            votes: increment(-1),
            [`votedBy.${participantId}`]: deleteField(),
          });
  
          transaction.set(
            participantRef,
            {
              votedIdeaId: "",
              votedAt: "",
            },
            { merge: true }
          );
  
          return;
        }
  
        if (previousVoteId) {
          const previousIdeaRef = doc(
            db,
            "sessions",
            sessionId,
            "ideas",
            previousVoteId
          );
  
          const previousIdeaSnapshot = await transaction.get(previousIdeaRef);
  
          if (previousIdeaSnapshot.exists()) {
            transaction.update(previousIdeaRef, {
              votes: increment(-1),
              [`votedBy.${participantId}`]: deleteField(),
            });
          }
        }
  
        transaction.update(selectedIdeaRef, {
          votes: increment(1),
          [`votedBy.${participantId}`]: true,
        });
  
        transaction.set(
          participantRef,
          {
            votedIdeaId: ideaId,
            votedAt: timeNow(),
            votedAtTimestamp: serverTimestamp(),
          },
          { merge: true }
        );
      });
  
      setParticipantVote((previousVoteId) =>
        previousVoteId === ideaId ? "" : ideaId
      );
  
      setVotedIdeas({});
    } catch (error) {
      console.error("Vote failed:", error);
      alert("Vote could not be saved. Please try again.");
    }
  }

  async function saveFinalIdea() {
    await setDoc(finalIdeaRef, {
      title: finalTitle,
      description: finalDescription,
      updatedAt: timeNow(),
      updatedAtTimestamp: serverTimestamp(),
    });
  
    alert("Final collaborative idea saved!");
  }
  
  function exportSession() {
    const sessionData = {
      condition: conditionLabel,
      sessionId,
      conditionCode: condition,
      designChallenge:
        "Design a solution that improves creative collaboration and idea selection in group brainwriting.",
      exportedAt: new Date().toISOString(),
      ideas,
      generalChat: chat,
      finalCollaborativeIdea: {
        title: finalTitle,
        description: finalDescription,
      },
    };

    const blob = new Blob([JSON.stringify(sessionData, null, 2)], {
      type: "application/json",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "human-anonymous-brainwriting-session.json";
    link.click();

    URL.revokeObjectURL(url);
  }

  if (accessStatus === "checking") {
    return (
      <main className="access-page">
        <section className="access-card">
          <div className="badge">
            <EyeOff size={16} />
            Checking Access
          </div>
          <h1>Please wait</h1>
          <p>Checking whether you have access to this study session...</p>
        </section>
      </main>
    );
  }
  
  if (accessStatus === "not_requested") {
    return (
      <main className="access-page">
        <section className="access-card">
          <div className="badge">
            <EyeOff size={16} />
            Restricted Study Access
          </div>
  
          <h1>Request Access</h1>
  
          <p>
            This study room is only for invited participants. Please enter your
            details and the password provided by the researcher.
          </p>
  
          <div className="access-session">
            Session: <strong>{sessionId}</strong>
            <br />
            Condition: <strong>{condition}</strong>
          </div>
  
          <form onSubmit={handleAccessSubmit} className="access-form">
            <input
              value={participantName}
              onChange={(e) => setParticipantName(e.target.value)}
              placeholder="Full name"
            />
  
            <input
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="Student ID"
            />
  
            <input
              value={accessCode}
              onChange={(e) => setAccessCode(e.target.value)}
              placeholder="Password"
              type="password"
            />
  
            <button type="submit" className="primary-button">
              Request Access
            </button>
          </form>
  
          {accessError && <div className="access-error">{accessError}</div>}
  
          <p className="access-note">
            Your name and student ID are collected only for researcher tracking.
            Inside the anonymous condition, your activity will still appear
            anonymous to other participants.
          </p>
        </section>
      </main>
    );
  }
  
  if (accessStatus === "pending") {
    return (
      <main className="access-page">
        <section className="access-card">
          <div className="badge">
            <EyeOff size={16} />
            Access Pending
          </div>
  
          <h1>Waiting for Approval</h1>
  
          <p>
            Your access request has been submitted. Please wait for the researcher
            to approve your access in Firebase, then refresh this page.
          </p>
  
          <div className="access-session">
            Session: <strong>{sessionId}</strong>
            <br />
            Name: <strong>{participantName}</strong>
            <br />
            Student ID: <strong>{studentId}</strong>
          </div>
  
          <button
            className="dark-button"
            onClick={() => window.location.reload()}
          >
            Refresh Access
          </button>
        </section>
      </main>
    );
  }
  
  return (
    <main className="app">
      <section className="hero">
        <div>
        <div className="badge">
          <EyeOff size={16} />
          {conditionLabel}
        </div>

        <h1>
          {isAnonymousCondition
            ? "Anonymous Brainwriting Room"
            : "Open Brainwriting Room"}
        </h1>

        <p>
          {isAnonymousCondition
            ? "Submit ideas anonymously, discuss each idea in its own thread, and use the general group chat to converge on one final direction."
            : "Submit ideas with your name visible, discuss each idea in its own thread, and use the general group chat to converge on one final direction."}
        </p>
        </div>

        <button className="dark-button" onClick={exportSession}>
          <Download size={18} />
          Export JSON
        </button>
      </section>

      <section className="challenge-box">
        <div>
          <span>Design Challenge</span>
          <h2>
            Design a solution that improves creative collaboration and idea selection
            in group brainwriting.
          </h2>
          {isAnonymousCondition ? (
            <p>
              First, submit your individual idea anonymously. Then discuss ideas in
              their threads, use the general chat to compare directions, and finally
              agree on one collaborative idea.
            </p>
          ) : (
            <p>
              First, submit your individual idea with your name visible. Then discuss
              ideas in their threads, use the general chat to compare directions, and
              finally agree on one collaborative idea.
            </p>
          )}
          <div className="session-pill">
            Active session: {sessionId}
          </div>
        </div>
      </section>

      <section className={isAnonymousCondition ? "mode-banner anonymous" : "mode-banner open"}>
        <div>
          <span>
            {isAnonymousCondition ? "Anonymous Mode" : "Open Mode"}
          </span>

          <h2>
            {isAnonymousCondition
              ? "Your identity is hidden from other participants."
              : "Your name is visible to other participants."}
          </h2>

          <p>
            {isAnonymousCondition
              ? "Your name and student ID are collected only for researcher tracking. Other participants will see your activity as anonymous."
              : "Your ideas, comments, chat messages, and votes will appear with your name so the group can discuss openly."}
          </p>
        </div>

        <div className="mode-user-pill">
          {isAnonymousCondition
            ? "Displayed as: Anonymous Participant"
            : `Displayed as: ${participantName || "Named Participant"}`}
        </div>
      </section>

      <section className="study-flow">
        <div className="study-flow-header">
          <span>Study Flow</span>
          <h2>Follow these steps during the session</h2>
        </div>

        <div className="flow-steps">
          <div className="flow-step">
            <strong>1</strong>
            <div>
              <h3>Submit</h3>
              <p>Add exactly one idea individually.</p>
            </div>
          </div>

          <div className="flow-step">
            <strong>2</strong>
            <div>
              <h3>Thread</h3>
              <p>Comment under specific ideas.</p>
            </div>
          </div>

          <div className="flow-step">
            <strong>3</strong>
            <div>
              <h3>Discuss</h3>
              <p>Use the group chat to compare ideas.</p>
            </div>
          </div>

          <div className="flow-step">
            <strong>4</strong>
            <div>
              <h3>Vote</h3>
              <p>Vote for one idea, but not your own.</p>
            </div>
          </div>

          <div className="flow-step">
            <strong>5</strong>
            <div>
              <h3>Converge</h3>
              <p>Write the final collaborative idea.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="rules-panel">
        <div className="rules-header">
          <span>Before You Start</span>
          <h2>Quick rules for this session</h2>
          <p>
            Please follow these simple rules so the discussion stays clear,
            respectful, and useful for the study.
          </p>
        </div>

        <div className="rules-list">
          <div className="rule-item">
            <strong>1</strong>
            <p>
              First, submit one original idea using [Original] in the title.
              After discussion, you may add collaborative ideas using
              [Collaborative] in the title. Please do not use AI; keep the
              ideas creative and original.
            </p>
          </div>

          <div className="rule-item">
            <strong>2</strong>
            <p>
              Vote for only one idea at a time. You may remove or change your vote, but you
              cannot vote for your own idea.
            </p>
          </div>

          <div className="rule-item">
            <strong>3</strong>
            <p>Comment constructively. You can suggest, improve, question, or combine ideas.</p>
          </div>

          <div className="rule-item">
            <strong>4</strong>
            <p>Use the group chat to compare ideas and agree on one final direction.</p>
          </div>

          <div className="rule-item">
            <strong>5</strong>
            <p>Keep the final collaborative idea short, clear, and understandable.</p>
          </div>
        </div>

        <div className="rules-note">
          {isAnonymousCondition
            ? "Anonymous condition: your name is hidden from other participants during ideas, comments, and chat."
            : "Open condition: your name will be visible with your ideas, comments, and chat messages."}
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <Lightbulb />
          <div>
            <strong>{ideas.length}</strong>
            <span>{isAnonymousCondition ? "Anonymous ideas" : "Named ideas"}</span>
          </div>
        </div>

        <div className="stat-card">
          <MessageCircle />
          <div>
            <strong>{totalComments}</strong>
            <span>Thread comments</span>
          </div>
        </div>

        <div className="stat-card">
          <Users />
          <div>
            <strong>{chat.length}</strong>
            <span>Group chat posts</span>
          </div>
        </div>

        <div className="stat-card">
          <Vote />
          <div>
            <strong>{totalVotes}</strong>
            <span>Total votes</span>
          </div>
        </div>
      </section>

      <section className="main-grid">
        <aside className="left-column">
          <div className="panel">
            <div className="panel-heading">
              <Plus size={20} />
              <div>
                <h2>
                  {isAnonymousCondition ? "Submit anonymous idea" : "Submit named idea"}
                </h2>
                <p>
                  {isAnonymousCondition
                    ? "No names are shown to participants."
                    : "Your name will be shown with your idea."}
                </p>
              </div>
            </div>

            <form className="form" onSubmit={submitIdea}>
              <input
                value={ideaTitle}
                onChange={(e) => setIdeaTitle(e.target.value)}
                placeholder="Idea title"
              />

              <textarea
                value={ideaBody}
                onChange={(e) => setIdeaBody(e.target.value)}
                placeholder="Describe your idea clearly..."
                rows="5"
              />

              <button className="primary-button" type="submit">
              {isAnonymousCondition ? "Add idea anonymously" : "Add named idea"}
              </button>

              <p className="form-note">
                Title format: use <strong>[Original]</strong> for your first individual idea
                and <strong>[Collaborative]</strong> for ideas created together after discussion.
              </p>
            </form>
          </div>

          <div className="panel">
            <h2>Idea board</h2>

            <div className="idea-list">
              {sortedIdeas.map((idea, index) => (
                <button
                  key={idea.id}
                  className={
                    activeIdeaId === idea.id ? "idea-card active" : "idea-card"
                  }
                  onClick={() => setActiveIdeaId(idea.id)}
                >
                  <div className="idea-card-top">
                    <div>
                      <span>Idea {index + 1}</span>
                      <h3>{idea.title}</h3>
                      <p className="idea-author">
                        {isAnonymousCondition
                          ? "Submitted anonymously"
                          : `Submitted by ${idea.authorName || idea.displayAuthor}`}
                      </p>
                    </div>

                    <strong>{idea.votes} votes</strong>
                  </div>

                  <p>{idea.body}</p>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="center-column">
          {activeIdea && (
            <div className="panel large-panel">
              <div className="idea-detail-top">
                <div>
                <span className="time-label">
                  {isAnonymousCondition
                    ? `Submitted anonymously at ${activeIdea.createdAt}`
                    : `Submitted by ${
                        activeIdea.authorName || activeIdea.displayAuthor
                      } at ${activeIdea.createdAt}`}
                </span>

                  <h2>{activeIdea.title}</h2>

                  <p>{activeIdea.body}</p>
                </div>

                <div className="idea-actions">
                  {activeIdeaIsOwn && (
                    <button
                      className="delete-button"
                      onClick={() => deleteOwnIdea(activeIdea.id)}
                    >
                      Delete My Idea
                    </button>
                  )}

                  <button
                    className={activeIdeaIsVoted ? "vote-button voted" : "vote-button"}
                    onClick={() => voteIdea(activeIdea.id)}
                    disabled={activeIdeaIsOwn}
                  >
                    {activeIdeaIsOwn ? (
                      "Cannot Vote Own Idea"
                    ) : activeIdeaIsVoted ? (
                      <>
                        <CheckCircle2 size={18} />
                        Remove Vote
                      </>
                    ) : hasVotedAnotherIdea ? (
                      <>
                        <Vote size={18} />
                        Change Vote
                      </>
                    ) : (
                      <>
                        <Vote size={18} />
                        Vote
                      </>
                    )}
                  </button>
                </div>
              </div>

              <div className="thread-box">
                <h3>
                  <MessageCircle size={18} />
                  Thread discussion
                </h3>

                <div className="comments">
                  {activeIdea.comments.length === 0 ? (
                    <div className="empty-box">
                      No thread comments yet. Start the debate for this idea.
                    </div>
                  ) : (
                    activeIdea.comments.map((comment) => (
                      <div className="message" key={comment.id}>
                        <div className="message-top">
                          <strong>{comment.author}</strong>
                          <span>{comment.time}</span>
                        </div>

                        <p>{comment.text}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="input-row">
                <input
                  value={commentDrafts[activeIdea.id] || ""}
                  onChange={(e) =>
                    setCommentDrafts((prev) => ({
                      ...prev,
                      [activeIdea.id]: e.target.value,
                    }))
                  }
                  placeholder={
                    isAnonymousCondition
                      ? "Write an anonymous critique, question, or improvement..."
                      : "Write a critique, question, or improvement..."
                  }
                />

                <button onClick={() => submitComment(activeIdea.id)}>
                  <Send size={18} />
                </button>
              </div>
            </div>
          )}
        </section>

        <aside className="right-column">
          <div className="panel large-panel chat-panel">
            <div className="panel-heading">
              <Users size={20} />
              <div>
                <h2>
                  {isAnonymousCondition ? "General anonymous chat" : "General group chat"}
                </h2>
                <p>Discuss patterns, compare ideas, and converge.</p>
              </div>
            </div>

            <div className="general-chat">
              {chat.map((message) => (
                <div className="message" key={message.id}>
                  <div className="message-top blue">
                    <strong>{message.author}</strong>
                    <span>{message.time}</span>
                  </div>

                  <p>{message.text}</p>
                </div>
              ))}
            </div>

            <form className="input-row" onSubmit={submitChat}>
              <input
                value={chatDraft}
                onChange={(e) => setChatDraft(e.target.value)}
                placeholder="Write in the general group chat..."
              />

              <button type="submit">
                <Send size={18} />
              </button>
            </form>
          </div>
        </aside>
      </section>
      
      <section className="final-panel">
        <div className="final-panel-header">
          <div>
            <span>Final Convergence</span>
            <h2>Final Collaborative Idea</h2>
            <p>
              As a group, agree on one final idea based on your discussion. Keep it
              short, clear, and understandable for someone who did not join your session.
              This final idea will be used for evaluation later.
            </p>
          </div>

          <button className="save-final-button" onClick={saveFinalIdea}>
            Save Final Idea
          </button>
        </div>

        <div className="final-form">
          <input
            value={finalTitle}
            onChange={(e) => setFinalTitle(e.target.value)}
            placeholder="Final idea title"
          />

          <textarea
            value={finalDescription}
            onChange={(e) => setFinalDescription(e.target.value)}
            placeholder="Describe the final collaborative idea clearly..."
            rows="5"
          />
        </div>
      </section>

      <section className="prototype-note">
      <strong>Study note:</strong> This session is connected to Firebase and stores
        ideas, comments, votes, chat messages, final decisions, and participant access
        records for the selected session.
      </section>
    </main>
  );
}

export default App;