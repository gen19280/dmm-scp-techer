import { useState, useEffect } from 'react';
import './App.css';

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

function App() {
  const [data, setData] = useState<Data | null>(null);
  const [availableTeachers, setAvailableTeachers] = useState<Teacher[]>([]);
  const [unavailableTeachers, setUnavailableTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState<{ section: SectionType; index: number } | null>(null);

  useEffect(() => {
    fetch(import.meta.env.BASE_URL + 'data.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('データの取得に失敗しました');
        }
        return response.json();
      })
      .then((result: Data) => {
        setData(result);
        setAvailableTeachers(result.teachers.filter(teacher => teacher.available));
        setUnavailableTeachers(result.teachers.filter(teacher => !teacher.available));
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

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

  if (loading) {
    return <div className="App">読み込み中...</div>;
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
