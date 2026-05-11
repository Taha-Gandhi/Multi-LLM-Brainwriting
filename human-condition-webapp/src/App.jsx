import { useMemo, useState } from "react";
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

function App() {
  const [ideas, setIdeas] = useState(initialIdeas);
  const [chat, setChat] = useState(initialChat);

  const [ideaTitle, setIdeaTitle] = useState("");
  const [ideaBody, setIdeaBody] = useState("");

  const [activeIdeaId, setActiveIdeaId] = useState(initialIdeas[0].id);
  const [commentDrafts, setCommentDrafts] = useState({});
  const [chatDraft, setChatDraft] = useState("");
  const [votedIdeas, setVotedIdeas] = useState({});
  const [finalTitle, setFinalTitle] = useState("");
  const [finalDescription, setFinalDescription] = useState("");

  const sortedIdeas = useMemo(() => {
    return [...ideas].sort((a, b) => b.votes - a.votes);
  }, [ideas]);

  const activeIdea = ideas.find((idea) => idea.id === activeIdeaId) || ideas[0];

  const totalComments = ideas.reduce(
    (total, idea) => total + idea.comments.length,
    0
  );

  const totalVotes = ideas.reduce((total, idea) => total + idea.votes, 0);

  function submitIdea(event) {
    event.preventDefault();

    if (!ideaTitle.trim() || !ideaBody.trim()) return;

    const newIdea = {
      id: `idea-${Date.now()}`,
      title: ideaTitle.trim(),
      body: ideaBody.trim(),
      createdAt: timeNow(),
      votes: 0,
      comments: [],
    };

    setIdeas((prev) => [newIdea, ...prev]);
    setActiveIdeaId(newIdea.id);
    setIdeaTitle("");
    setIdeaBody("");
  }

  function submitComment(ideaId) {
    const text = commentDrafts[ideaId]?.trim();

    if (!text) return;

    setIdeas((prevIdeas) =>
      prevIdeas.map((idea) => {
        if (idea.id !== ideaId) return idea;

        return {
          ...idea,
          comments: [
            ...idea.comments,
            {
              id: Date.now(),
              author: anonymousName(),
              text,
              time: timeNow(),
            },
          ],
        };
      })
    );

    setCommentDrafts((prev) => ({
      ...prev,
      [ideaId]: "",
    }));
  }

  function submitChat(event) {
    event.preventDefault();

    if (!chatDraft.trim()) return;

    setChat((prev) => [
      ...prev,
      {
        id: Date.now(),
        author: anonymousName(),
        text: chatDraft.trim(),
        time: timeNow(),
      },
    ]);

    setChatDraft("");
  }

  function voteIdea(ideaId) {
    if (votedIdeas[ideaId]) return;

    setIdeas((prevIdeas) =>
      prevIdeas.map((idea) => {
        if (idea.id !== ideaId) return idea;
        return {
          ...idea,
          votes: idea.votes + 1,
        };
      })
    );

    setVotedIdeas((prev) => ({
      ...prev,
      [ideaId]: true,
    }));
  }

  function exportSession() {
    const sessionData = {
      condition: "Human Anonymous Brainwriting",
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

  return (
    <main className="app">
      <section className="hero">
        <div>
          <div className="badge">
            <EyeOff size={16} />
            Anonymous Human Condition
          </div>

          <h1>Anonymous Brainwriting Room</h1>

          <p>
            Submit ideas anonymously, discuss each idea in its own thread, and
            use the general group chat to converge on one final direction.
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
          <p>
            First, submit your individual idea anonymously. Then discuss ideas in
            their threads, use the general chat to compare directions, and finally
            agree on one collaborative idea.
          </p>
        </div>
      </section>

      <section className="instructions-grid">
        <div>
          <strong>1. Submit</strong>
          <p>Write one idea anonymously. Do not include your name.</p>
        </div>

        <div>
          <strong>2. Discuss</strong>
          <p>Comment under each idea thread with critique, questions, or improvements.</p>
        </div>

        <div>
          <strong>3. Debate</strong>
          <p>Use the general chat to compare ideas and negotiate a stronger direction.</p>
        </div>

        <div>
          <strong>4. Converge</strong>
          <p>Write the final collaborative idea in the final decision panel.</p>
        </div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <Lightbulb />
          <div>
            <strong>{ideas.length}</strong>
            <span>Anonymous ideas</span>
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
                <h2>Submit anonymous idea</h2>
                <p>No names are shown to participants.</p>
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
                Add idea anonymously
              </button>
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
                    Submitted anonymously at {activeIdea.createdAt}
                  </span>

                  <h2>{activeIdea.title}</h2>

                  <p>{activeIdea.body}</p>
                </div>

                <button
                  className={
                    votedIdeas[activeIdea.id]
                      ? "vote-button voted"
                      : "vote-button"
                  }
                  onClick={() => voteIdea(activeIdea.id)}
                  disabled={votedIdeas[activeIdea.id]}
                >
                  {votedIdeas[activeIdea.id] ? (
                    <>
                      <CheckCircle2 size={18} />
                      Voted
                    </>
                  ) : (
                    <>
                      <Vote size={18} />
                      Vote
                    </>
                  )}
                </button>
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
                  placeholder="Write an anonymous critique, question, or improvement..."
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
                <h2>General anonymous chat</h2>
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
              After the discussion, the group should agree on one final idea here.
              This will be exported for blind evaluation later.
            </p>
          </div>
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
        <strong>Prototype note:</strong> This quick version stores data in the
        browser only. For the real study, connect it to Firebase, Supabase, or a
        small backend so multiple participants can join live and data persists.
      </section>
    </main>
  );
}

export default App;