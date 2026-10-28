import json, os, sqlite3, uuid
from datetime import datetime, timezone
from pathlib import Path

def _now(): return datetime.now(timezone.utc).isoformat()

class Repository:
    def __init__(self, path=None):
        self.path = path or os.getenv("MYSTERYX_DB_PATH", "mysteryx.sqlite3")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init()
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db
    def _init(self):
        with self.connect() as d:
            d.executescript('''
            CREATE TABLE IF NOT EXISTS cases(case_id TEXT PRIMARY KEY,title TEXT,premise TEXT,difficulty TEXT,public_case_json TEXT,private_solution_json TEXT,created_at TEXT,schema_version INTEGER,status TEXT);
            CREATE TABLE IF NOT EXISTS sessions(session_id TEXT PRIMARY KEY,case_id TEXT REFERENCES cases(case_id),status TEXT,current_page TEXT,created_at TEXT,updated_at TEXT);
            CREATE TABLE IF NOT EXISTS discoveries(session_id TEXT REFERENCES sessions(session_id),clue_id TEXT,discovered_at TEXT,UNIQUE(session_id,clue_id));
            CREATE TABLE IF NOT EXISTS hint_usage(session_id TEXT REFERENCES sessions(session_id),hint_id TEXT,used_at TEXT,UNIQUE(session_id,hint_id));
            CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,session_id TEXT REFERENCES sessions(session_id),suspect_id TEXT,role TEXT,message TEXT,created_at TEXT);
            CREATE TABLE IF NOT EXISTS results(session_id TEXT UNIQUE REFERENCES sessions(session_id),selected_suspect_id TEXT,reasoning_text TEXT,is_correct INTEGER,base_points INTEGER,clue_points INTEGER,hint_penalties INTEGER,final_score INTEGER,submitted_at TEXT);
            CREATE TABLE IF NOT EXISTS case_translations(case_id TEXT REFERENCES cases(case_id),language TEXT,translated_json TEXT,created_at TEXT,PRIMARY KEY(case_id,language));
            ''')
    def save_case(self, case, language="English"):
        cid = str(uuid.uuid4()); data = case.model_dump(mode="json"); data["case_id"] = cid
        from .models import GeneratedCase
        case = GeneratedCase.model_validate(data)
        public = {"case_id":cid,"title":case.title,"premise":case.premise,"difficulty":case.difficulty.value,"story":case.story,"language":language,
                  "suspects":[s.model_dump(include={"id","name","profile","motive","public_alibi"}) for s in case.suspects],
                  "clues":[c.model_dump(include={"id","title","description","details","implicates_suspect_ids"}) for c in case.clues],
                  "hints":[h.model_dump() for h in case.hints]}
        private = {"solution":case.solution.model_dump(),"suspect_truths":{s.id:s.private_truth for s in case.suspects},
                   "clue_relevance":{c.id:c.solution_relevance for c in case.clues},"timeline":[t.model_dump() for t in case.timeline]}
        with self.connect() as d:
            d.execute("INSERT INTO cases VALUES(?,?,?,?,?,?,?,?,?)",(cid,case.title,case.premise,case.difficulty.value,json.dumps(public),json.dumps(private),_now(),1,"accepted"))
            sid = str(uuid.uuid4()); d.execute("INSERT INTO sessions VALUES(?,?, 'investigating','investigation',?,?)",(sid,cid,_now(),_now()))
        return sid
    def active_session(self):
        with self.connect() as d:
            row=d.execute("SELECT session_id FROM sessions WHERE status='investigating' ORDER BY updated_at DESC LIMIT 1").fetchone()
            return row[0] if row else None
    def get_game(self,sid):
        with self.connect() as d:
            row=d.execute("SELECT s.*,c.public_case_json,c.private_solution_json FROM sessions s JOIN cases c USING(case_id) WHERE session_id=?",(sid,)).fetchone()
            if not row: return None
            game=dict(row); game["case"]=json.loads(game.pop("public_case_json")); private=json.loads(game.pop("private_solution_json")); game["solution"]=private["solution"]
            for suspect in game["case"]["suspects"]: suspect["private_truth"]=private["suspect_truths"][suspect["id"]]
            for clue in game["case"]["clues"]: clue["solution_relevance"]=private["clue_relevance"][clue["id"]]
            game["case"]["timeline"]=private["timeline"]
            game["discoveries"]=[r[0] for r in d.execute("SELECT clue_id FROM discoveries WHERE session_id=?",(sid,))]
            game["hints_used"]=[r[0] for r in d.execute("SELECT hint_id FROM hint_usage WHERE session_id=?",(sid,))]
            game["messages"]=[dict(r) for r in d.execute("SELECT suspect_id,role,message,created_at FROM messages WHERE session_id=? ORDER BY id",(sid,))]
            game["result"]=d.execute("SELECT * FROM results WHERE session_id=?",(sid,)).fetchone()
            return game
    def list_solved_cases(self):
        """Return completed investigations only; never expose active solutions in history."""
        with self.connect() as d:
            rows=d.execute('''
                SELECT s.session_id,r.submitted_at,r.selected_suspect_id,r.is_correct,
                       r.base_points,r.clue_points,r.hint_penalties,r.final_score,
                       c.public_case_json,c.private_solution_json
                FROM sessions s
                JOIN results r ON r.session_id=s.session_id
                JOIN cases c ON c.case_id=s.case_id
                WHERE s.status='completed'
                ORDER BY r.submitted_at DESC
            ''').fetchall()
            solved=[]
            for row in rows:
                case=json.loads(row["public_case_json"])
                private=json.loads(row["private_solution_json"])
                case["timeline"]=private["timeline"]
                clues={clue["id"]:clue for clue in case["clues"]}
                suspects={suspect["id"]:suspect for suspect in case["suspects"]}
                solved.append({
                    "session_id":row["session_id"],
                    "case":case,
                    "solution":private["solution"],
                    "result":{key:row[key] for key in ("submitted_at","selected_suspect_id","is_correct","base_points","clue_points","hint_penalties","final_score")},
                    "chosen_suspect":suspects.get(row["selected_suspect_id"]),
                    "culprit":suspects.get(private["solution"]["culprit_id"]),
                    "supporting_clues":[clues[cid] for cid in private["solution"]["supporting_clue_ids"] if cid in clues],
                })
            return solved
    def get_case_translation(self,case_id,language):
        with self.connect() as d:
            row=d.execute("SELECT translated_json FROM case_translations WHERE case_id=? AND language=?",(case_id,language)).fetchone()
            return json.loads(row[0]) if row else None
    def save_case_translation(self,case_id,language,translated):
        with self.connect() as d:
            d.execute("INSERT INTO case_translations VALUES(?,?,?,?) ON CONFLICT(case_id,language) DO UPDATE SET translated_json=excluded.translated_json,created_at=excluded.created_at",(case_id,language,json.dumps(translated,ensure_ascii=False),_now()))
    def discover(self,sid,cid):
        with self.connect() as d: return d.execute("INSERT OR IGNORE INTO discoveries VALUES(?,?,?)",(sid,cid,_now())).rowcount == 1
    def use_hint(self,sid,hid):
        with self.connect() as d: return d.execute("INSERT OR IGNORE INTO hint_usage VALUES(?,?,?)",(sid,hid,_now())).rowcount == 1
    def add_message(self,sid,suspect,role,message):
        with self.connect() as d: d.execute("INSERT INTO messages(session_id,suspect_id,role,message,created_at) VALUES(?,?,?,?,?)",(sid,suspect,role,message,_now()))
    def submit(self,sid,suspect,reasoning,result):
        with self.connect() as d:
            existing=d.execute("SELECT * FROM results WHERE session_id=?",(sid,)).fetchone()
            if existing: return dict(existing)
            game=d.execute("SELECT c.public_case_json,c.private_solution_json FROM sessions s JOIN cases c USING(case_id) WHERE session_id=? AND s.status='investigating'",(sid,)).fetchone()
            if not game: raise ValueError("Invalid session")
            case=json.loads(game[0]); solution=json.loads(game[1])["solution"]; suspect_ids={x['id'] for x in case['suspects']}
            if suspect not in suspect_ids: raise ValueError("Invalid suspect")
            row=d.execute("SELECT COUNT(*) FROM discoveries WHERE session_id=?",(sid,)).fetchone()[0]; hints=d.execute("SELECT COUNT(*) FROM hint_usage WHERE session_id=?",(sid,)).fetchone()[0]
            vals=result(solution['culprit_id']==suspect,row,hints)
            d.execute("INSERT INTO results VALUES(?,?,?,?,?,?,?,?,?)",(sid,suspect,reasoning,int(solution['culprit_id']==suspect),vals['base_points'],vals['clue_points'],vals['hint_penalties'],vals['final_score'],_now()))
            d.execute("UPDATE sessions SET status='completed',current_page='results',updated_at=? WHERE session_id=?",(_now(),sid))
            return dict(d.execute("SELECT * FROM results WHERE session_id=?",(sid,)).fetchone())
    def new_case(self, sid):
        if sid:
            with self.connect() as d: d.execute("UPDATE sessions SET status='archived',updated_at=? WHERE session_id=?",(_now(),sid))
