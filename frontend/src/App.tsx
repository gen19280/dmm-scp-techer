import { useState, useEffect } from 'react';
import './App.css';
import { initializeApp } from 'firebase/app';
import {
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
  GoogleAuthProvider
} from 'firebase/auth';
import type { User } from 'firebase/auth';

interface Teacher {
  name: string;
  url: string;
  image_url: string | null;
  available: boolean;
}

interface Data {
  last_updated: string;
  teachers: Teacher[];
}

type SectionType = 'available' | 'unavailable';

const firebaseConfig = {
  apiKey: 'AIzaSyCebgViIftPo9n8vA4BEHHOY7rYnob29Mc',
  authDomain: 'dmm-scp-techer.firebaseapp.com',
  projectId: 'dmm-scp-techer',
  storageBucket: 'dmm-scp-techer.firebasestorage.app',
  messagingSenderId: '769506593095',
  appId: '1:769506593095:web:9dc12e1e6ebd7b10f7e462',
  measurementId: 'G-KD1LKYQRHZ'
};

function App() {
  const [data, setData] = useState<Data | null>(null);
  const [availableTeachers, setAvailableTeachers] = useState<Teacher[]>([]);
  const [unavailableTeachers, setUnavailableTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true); // data loading state
  const [authLoading, setAuthLoading] = useState(true); // auth state
  const [authAttempted, setAuthAttempted] = useState(false); // popup once
  const [error, setError] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [accessDenied, setAccessDenied] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [dragging, setDragging] = useState<{ section: SectionType; index: number } | null>(null);

  const handleSignOut = async () => {
    const auth = getAuth();
    try {
      await signOut(auth);
      setUser(null);
      setAccessDenied(false);
      setAuthError(null);
      setAuthAttempted(false);
      setLoading(true);
      setData(null);
      setAvailableTeachers([]);
      setUnavailableTeachers([]);
    } catch (err: any) {
      setAuthError(err?.message || 'サインアウト中にエラーが発生しました');
    }
  };

  const fetchTeacherData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(import.meta.env.BASE_URL + 'data.json');
      if (!response.ok) {
        throw new Error('データの取得に失敗しました');
      }
      const result = (await response.json()) as Data;
      setData(result);
      setAvailableTeachers(result.teachers.filter(teacher => teacher.available));
      setUnavailableTeachers(result.teachers.filter(teacher => !teacher.available));
    } catch (err: any) {
      setError(err.message || 'データの読み込み中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);

    const unsubscribe = onAuthStateChanged(
      auth,
      (currentUser: User | null) => {
        if (!currentUser) {
          setUser(null);
          setAuthLoading(false);
          return;
        }

        setUser(currentUser);

        setAccessDenied(false);
        setAuthError(null);
        setAuthLoading(false);
        fetchTeacherData();
      },
      (authErr: Error) => {
        setAuthError(authErr.message || '認証状態の処理中にエラーが発生しました');
        setAuthLoading(false);
      }
    );

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    const auth = getAuth();
    const provider = new GoogleAuthProvider();

    if (!authLoading && !user && !authAttempted && !accessDenied) {
      setAuthAttempted(true);
      signInWithPopup(auth, provider)
        .then(result => {
          const signedUser = result.user;
          setUser(signedUser);
        })
        .catch(err => {
          setAuthError(err?.message || 'サインイン中にエラーが発生しました');
          setAuthLoading(false);
        });
    }
  }, [authLoading, user, authAttempted, accessDenied]);

  const handleDragStart = (section: SectionType, index: number) => (event: React.DragEvent<HTMLLIElement>) => {
    setDragging({ section, index });
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (event: React.DragEvent<HTMLLIElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const handleDragEnd = () => {
    setDragging(null);
  };

  const reorder = (list: Teacher[], fromIndex: number, toIndex: number) => {
    const updated = [...list];
    const [moved] = updated.splice(fromIndex, 1);
    updated.splice(toIndex, 0, moved);
    return updated;
  };

  const handleDrop = (section: SectionType, index: number) => (event: React.DragEvent<HTMLLIElement>) => {
    event.preventDefault();
    if (!dragging || dragging.section !== section) {
      return;
    }

    if (section === 'available') {
      setAvailableTeachers(prev => reorder(prev, dragging.index, index));
    } else {
      setUnavailableTeachers(prev => reorder(prev, dragging.index, index));
    }

    setDragging(null);
  };

  if (authLoading) {
    return <div className="App">認証処理中...</div>;
  }

  if (authError) {
    return <div className="App">認証エラー: {authError}</div>;
  }

  if (accessDenied) {
    return <div className="App">アクセス拒否: このサイトにアクセスできるのは saryupointo@gmail.com のみです。</div>;
  }

  if (loading) {
    return <div className="App">データ読み込み中...</div>;
  }

  if (error) {
    return <div className="App">エラー: {error}</div>;
  }

  if (!data) {
    return <div className="App">データがありません</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>DMM英会話 予約可能講師一覧</h1>
        <p>最終更新: {new Date(data.last_updated).toLocaleString('ja-JP')}</p>
        {user && <p>ログインユーザー: {user.email}</p>}
        {user && (
          <button className="signout-btn" onClick={handleSignOut}>
            サインアウト
          </button>
        )}
      </header>

      <main>
        <section>
          <h2>予約可能な講師 ({availableTeachers.length}名)</h2>
          {availableTeachers.length > 0 ? (
            <ul className="teacher-list available">
              {availableTeachers.map((teacher, index) => {
                const isDragging = dragging?.section === 'available' && dragging.index === index;
                return (
                  <li
                    key={teacher.url || `${teacher.name}-${index}`}
                    className={`teacher-item ${isDragging ? 'dragging' : ''}`}
                    draggable
                    onDragStart={handleDragStart('available', index)}
                    onDragOver={handleDragOver}
                    onDrop={handleDrop('available', index)}
                    onDragEnd={handleDragEnd}
                  >
                    {teacher.image_url && (
                      <img src={teacher.image_url} alt={teacher.name} className="teacher-image" />
                    )}
                    <div className="teacher-info">
                      <a href={teacher.url} target="_blank" rel="noopener noreferrer">
                        {teacher.name}
                      </a>
                      <span className="status available">予約可</span>
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p>現在予約可能な講師はいません。</p>
          )}
        </section>

        <section>
          <h2>予約不可の講師 ({unavailableTeachers.length}名)</h2>
          <ul className="teacher-list unavailable">
            {unavailableTeachers.map((teacher, index) => {
              const isDragging = dragging?.section === 'unavailable' && dragging.index === index;
              return (
                <li
                  key={teacher.url || `${teacher.name}-${index}`}
                  className={`teacher-item ${isDragging ? 'dragging' : ''}`}
                  draggable
                  onDragStart={handleDragStart('unavailable', index)}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop('unavailable', index)}
                  onDragEnd={handleDragEnd}
                >
                  {teacher.image_url && (
                    <img src={teacher.image_url} alt={teacher.name} className="teacher-image" />
                  )}
                  <div className="teacher-info">
                    <a href={teacher.url} target="_blank" rel="noopener noreferrer">
                      {teacher.name}
                    </a>
                    <span className="status unavailable">予約不可</span>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      </main>
    </div>
  );
}

export default App;
