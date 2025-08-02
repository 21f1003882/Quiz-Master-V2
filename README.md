erDiagram
    %% Entities and Attributes
    USER {
        int id PK "User ID"
        string username UK "Unique Username"
        string email UK "Unique Email"
        string password_hash "Hashed Password"
        datetime created_at "Creation Timestamp"
        boolean active "Is account active?"
        string fs_uniquifier UK "Flask-Security Unique ID"
    }

    ROLE {
        int id PK "Role ID"
        string name UK "Role Name (e.g., admin, user)"
        string description "Optional Description"
    }

    user_roles {
        int user_id PK, FK "Foreign Key to User"
        int role_id PK, FK "Foreign Key to Role"
    }

    SUBJECT {
        int id PK "Subject ID"
        string name UK "Unique Subject Name"
        string description "Optional Description"
        datetime created_at "Creation Timestamp"
    }

    CHAPTER {
        int id PK "Chapter ID"
        string name "Chapter Name"
        int subject_id FK "Foreign Key to Subject"
        datetime created_at "Creation Timestamp"
    }

    QUIZ {
        int id PK "Quiz ID"
        string title "Quiz Title"
        int chapter_id FK "Foreign Key to Chapter"
        datetime created_at "Creation Timestamp"
        int duration_minutes "Quiz Duration"
        boolean is_active "Is quiz available?"
    }

    QUESTION {
        int id PK "Question ID"
        string text "Question Text"
        int quiz_id FK "Foreign Key to Quiz"
    }

    OPTION {
        int id PK "Option ID"
        string text "Option Text"
        boolean is_correct "Is this the correct option?"
        int question_id FK "Foreign Key to Question"
    }

    QUIZ_ATTEMPT {
        int id PK "Attempt ID"
        int user_id FK "Foreign Key to User"
        int quiz_id FK "Foreign Key to Quiz"
        int score "Score Achieved"
        int total_questions "Total Questions in Quiz at time of attempt"
        datetime start_time "Timestamp when attempt started (UTC)"
        datetime submitted_at "Timestamp when attempt submitted (UTC)"
    }

    %% Relationships
    USER ||--o{ user_roles : "maps to roles via"
    ROLE ||--o{ user_roles : "maps to users via"
    USER ||--o{ QUIZ_ATTEMPT : "performs"
    SUBJECT ||--o{ CHAPTER : "contains"
    CHAPTER ||--o{ QUIZ : "contains"
    QUIZ ||--o{ QUESTION : "contains"
    QUIZ ||--o{ QUIZ_ATTEMPT : "is subject of"
    QUESTION ||--o{ OPTION : "has"