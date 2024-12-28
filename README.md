# InstaPy

Welcome to **InstaPy**, a feature-rich, Instagram-like web application built with **FastAPI** and **MongoDB**. InstaPy allows users to create accounts, share posts with images and captions, follow other users, like and comment on posts, and explore content through powerful search and filtering capabilities. Whether you're looking to connect with friends, share your experiences, or discover new content, InstaPy provides a seamless and engaging platform to do so.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Demo](#demo)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Directory Structure](#directory-structure)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

## Features

- **User Authentication:**
  - **Registration:** Create a new account with a unique username and email.
  - **Login:** Securely log in using your credentials.
  - **Logout:** Safely log out from your account.

- **User Profiles:**
  - View personal and other users' profiles.
  - Display follower and following counts.
  - Follow and unfollow other users.

- **Posts:**
  - **Create Posts:** Share images with captions and categorize them.
  - **View Posts:** Browse through a personalized feed of posts from followed users.
  - **Like & Unlike:** Express appreciation by liking posts.
  - **Comment:** Engage with posts by leaving comments.

- **Search & Explore:**
  - **Search Users:** Find other users by their usernames.
  - **Search Posts:** Discover posts using hashtags, categories, and date filters.

- **Pagination:**
  - Efficiently navigate through large sets of users, posts, likes, and comments with pagination controls.

- **Responsive Design:**
  - A clean and modern interface that adapts seamlessly to various screen sizes and devices.

- **Secure Data Handling:**
  - Passwords are hashed using bcrypt for enhanced security.
  - JWT-based authentication with HTTP-only cookies to protect user sessions.

- **Logging:**
  - Comprehensive logging of important events and errors to aid in monitoring and debugging.

## Technology Stack

- **Backend:**
  - [FastAPI](https://fastapi.tiangolo.com/) - A modern, fast (high-performance) web framework for building APIs with Python.
  - [Motor](https://motor.readthedocs.io/en/stable/) - An asynchronous Python driver for MongoDB.
  - [Python-JOSE](https://python-jose.readthedocs.io/en/latest/) - A Python library for handling JWT tokens.
  - [bcrypt](https://pypi.org/project/bcrypt/) - For hashing and verifying passwords.
  - [Python-Dotenv](https://pypi.org/project/python-dotenv/) - To load environment variables from a `.env` file.

- **Frontend:**
  - **Templates:** Jinja2 templates for rendering dynamic HTML pages.
  - **CSS:** Custom CSS for styling and responsive design.

- **Database:**
  - [MongoDB](https://www.mongodb.com/) - A NoSQL database for storing user data, posts, comments, likes, and more.

- **Other Tools:**
  - [Uvicorn](https://www.uvicorn.org/) - A lightning-fast ASGI server for Python.
  - [Git](https://git-scm.com/) - Version control system.

## Demo

![image](https://github.com/user-attachments/assets/eebcfa0e-eb46-44c0-a2be-2b5a02f94d0d)

![Screenshot 2024-12-28 175149](https://github.com/user-attachments/assets/d876aeb5-6414-4fff-ba8b-b5e68ca82855)

![image](https://github.com/user-attachments/assets/adc51eec-5069-468a-8b66-da00ca57b3a2)

![image](https://github.com/user-attachments/assets/da641235-7871-4305-892c-350af5458392)


![image](https://github.com/user-attachments/assets/28b2a3d2-582d-4c8b-8063-52d1768d9a71)

![image](https://github.com/user-attachments/assets/8101345d-5c6f-46a0-9484-88da80064602)

![image](https://github.com/user-attachments/assets/4d7b1531-4a35-484d-bc51-4157911c46b0)


## Installation

Follow the steps below to set up and run InstaPy on your local machine.

### Prerequisites

- **Python 3.11** or higher
- **MongoDB** installed and running locally or accessible remotely
- **Git** installed

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/instaPy.git
   cd instaPy
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**

   - **Windows (PowerShell):**

     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

   - **Windows (Command Prompt):**

     ```cmd
     .\venv\Scripts\activate.bat
     ```

   - **Unix or MacOS:**

     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables:**

   - Create a `.env` file in the root directory of the project with the following content:

     ```env
     MONGO_URI=mongodb://localhost:27017
     DATABASE_NAME=instagram
     SECRET_KEY=your_secret_key_here
     ```

   - **Replace `your_secret_key_here`** with a strong, unique secret key. You can generate one using Python:

     ```python
     import secrets
     print(secrets.token_urlsafe(32))
     ```

6. **Prepare Static Files:**

   - Ensure that the `static/images/` directory exists to store uploaded images.

     ```bash
     mkdir -p static/images
     ```

## Configuration

- **Environment Variables:**

  - `MONGO_URI`: The connection string for your MongoDB instance.
  - `DATABASE_NAME`: The name of the MongoDB database to use.
  - `SECRET_KEY`: A secret key for encoding JWT tokens. **Keep this secure and do not expose it.**

- **Static Files:**

  - **CSS:** Located in `static/css/styles.css`.
  - **Images:** Uploaded images are stored in `static/images/`.

## Running the Application

1. **Activate the Virtual Environment:**

   Ensure you're in the project's root directory and the virtual environment is activated.

   ```bash
   # For Windows (PowerShell)
   .\venv\Scripts\Activate.ps1

   # For Unix or MacOS
   source venv/bin/activate
   ```

2. **Start the Uvicorn Server:**

   ```bash
   uvicorn app:app --reload
   ```

   - The `--reload` flag enables auto-reloading on code changes.
   - Access the application at [http://127.0.0.1:8000](http://127.0.0.1:8000).

3. **Accessing the Application:**

   - **Home Page:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Register:** [http://127.0.0.1:8000/register](http://127.0.0.1:8000/register)
   - **Login:** [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)
   - **Feed:** [http://127.0.0.1:8000/feed](http://127.0.0.1:8000/feed) (Requires login)
   - **Create Post:** [http://127.0.0.1:8000/create_post](http://127.0.0.1:8000/create_post) (Requires login)
   - **Search Users:** [http://127.0.0.1:8000/search_users](http://127.0.0.1:8000/search_users) (Requires login)
   - **Search Posts:** [http://127.0.0.1:8000/search_posts](http://127.0.0.1:8000/search_posts) (Requires login)

## Directory Structure

```
instaPy/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── profile.html
│   ├── create_post.html
│   ├── feed.html
│   ├── post_detail.html
│   ├── search_users.html
│   ├── search_posts.html
│   ├── post_likes.html
│   └── post_comments.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── images/
│       └── (uploaded images)
├── requirements.txt
├── .env
└── README.md
```

- **app/**: Contains the backend application code.
  - `__init__.py`: Initializes the FastAPI app and mounts static files.
  - `auth.py`: Handles authentication and user session management.
  - `database.py`: Manages database connections and initializes indexes.
  - `main.py`: Defines API routes and business logic.
  - `models.py`: Defines data models using Pydantic.

- **templates/**: Contains Jinja2 HTML templates for rendering pages.

- **static/**: Serves static files like CSS and uploaded images.
  - `css/styles.css`: Custom styles for the application.
  - `images/`: Directory to store uploaded images.

- **requirements.txt**: Lists all Python dependencies.

- **.env**: Stores environment variables.

- **README.md**: This file.

## Usage

### 1. **Register a New Account**

- Navigate to the [Register](http://127.0.0.1:8000/register) page.
- Fill in your desired username, email, and password.
- Submit the form to create your account.

### 2. **Login**

- After registering, go to the [Login](http://127.0.0.1:8000/login) page.
- Enter your username and password.
- Upon successful login, you'll be redirected to your personalized feed.

### 3. **Create a Post**

- Access the [Create Post](http://127.0.0.1:8000/create_post) page.
- Upload an image, add a caption, and specify a category.
- Submit the form to share your post with others.

### 4. **View Your Feed**

- Visit the [Feed](http://127.0.0.1:8000/feed) to see posts from users you follow.
- Like, unlike, and comment on posts directly from your feed.

### 5. **Profile Management**

- Access your profile at [Profile](http://127.0.0.1:8000/profile/) to view your posts and follower statistics.
- Follow or unfollow other users from their profiles.

### 6. **Search and Explore**

- **Search Users:** Navigate to [Search Users](http://127.0.0.1:8000/search_users) to find other users by their usernames.
- **Search Posts:** Go to [Search Posts](http://127.0.0.1:8000/search_posts) to discover posts using hashtags, categories, and date filters.

### 7. **Logout**

- Click on the **Logout** link in the navigation bar to end your session.

## API Endpoints

Here's a summary of the main API endpoints available in InstaPy:

| Method | Endpoint                | Description                                         | Authentication |
| ------ | ----------------------- | --------------------------------------------------- | --------------- |
| GET    | `/`                     | Home page                                           | Optional        |
| GET    | `/register`             | Registration page                                   | Optional        |
| POST   | `/register`             | Handle user registration                            | Optional        |
| GET    | `/login`                | Login page                                          | Optional        |
| POST   | `/login`                | Handle user login                                   | Optional        |
| GET    | `/logout`               | Logout user                                         | Optional        |
| GET    | `/profile/{user_id}`    | View a user's profile                               | Required        |
| GET    | `/profile/`             | Redirect to current user's profile                  | Required        |
| GET    | `/create_post`          | Create a new post page                              | Required        |
| POST   | `/create_post`          | Handle new post creation                            | Required        |
| GET    | `/feed`                 | View personalized feed of posts                     | Required        |
| GET    | `/posts/{post_id}`      | View detailed post page                             | Required        |
| POST   | `/like/{post_id}`       | Like or unlike a post                               | Required        |
| POST   | `/comment/{post_id}`    | Add a comment to a post                             | Required        |
| POST   | `/follow/{user_id}`     | Follow or unfollow a user                            | Required        |
| GET    | `/search_users`         | Search for users by username                        | Required        |
| GET    | `/search_posts`         | Search for posts by hashtag, category, and date      | Required        |
| GET    | `/posts/{post_id}/likes`| View list of users who liked a post                  | Required        |
| GET    | `/posts/{post_id}/comments` | View list of comments on a post                | Required        |

### Detailed Endpoint Descriptions

1. **Home Page (`GET /`):**
   - Renders the landing page of the application.
   - Shows welcome message and navigation links based on authentication status.

2. **User Registration (`GET /register`, `POST /register`):**
   - **GET:** Displays the registration form.
   - **POST:** Handles form submission, validates input, hashes password, and creates a new user in the database.

3. **User Login (`GET /login`, `POST /login`):**
   - **GET:** Displays the login form.
   - **POST:** Authenticates user credentials, generates JWT token, and sets it in an HTTP-only cookie.

4. **User Logout (`GET /logout`):**
   - Clears the authentication cookie and redirects to the home page.

5. **User Profile (`GET /profile/{user_id}`, `GET /profile/`):**
   - **GET /profile/{user_id}:** Displays the profile of the specified user, including their posts, followers, and following lists.
   - **GET /profile/:** Redirects to the current authenticated user's profile.

6. **Create Post (`GET /create_post`, `POST /create_post`):**
   - **GET:** Displays the form to create a new post.
   - **POST:** Handles post creation, saves uploaded image, extracts hashtags, and stores post data in the database.

7. **Feed (`GET /feed`):**
   - Displays a feed of posts from users the current user follows.
   - Includes pagination for navigating through posts.

8. **Post Details (`GET /posts/{post_id}`):**
   - Displays detailed information about a specific post, including likes and comments.
   - Allows the user to like/unlike and comment on the post.

9. **Like/Unlike Post (`POST /like/{post_id}`):**
   - Toggles the like status of a post for the current user.

10. **Comment on Post (`POST /comment/{post_id}`):**
    - Adds a comment to a specific post.

11. **Follow/Unfollow User (`POST /follow/{user_id}`):**
    - Allows the current user to follow or unfollow another user.

12. **Search Users (`GET /search_users`):**
    - Enables searching for users by their usernames with pagination support.

13. **Search Posts (`GET /search_posts`):**
    - Enables searching for posts by hashtags, categories, and date ranges with pagination support.

14. **View Post Likes (`GET /posts/{post_id}/likes`):**
    - Displays a paginated list of users who have liked a specific post.

15. **View Post Comments (`GET /posts/{post_id}/comments`):**
    - Displays a paginated list of comments on a specific post.

## Contributing

Contributions are welcome! If you'd like to contribute to InstaPy, please follow these guidelines:

1. **Fork the Repository:**

   Click the "Fork" button at the top-right corner of the repository page.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/yourusername/instaPy.git
   cd instaPy
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:**

   Implement your feature or bug fix.

5. **Commit Your Changes:**

   ```bash
   git add .
   git commit -m "Add Your Feature Description"
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Open a Pull Request:**

   Navigate to your forked repository on GitHub and click the "New pull request" button.



## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used.
- [Motor](https://motor.readthedocs.io/en/stable/) - Asynchronous MongoDB driver.
- [Jinja2](https://jinja.palletsprojects.com/) - Templating engine for Python.
- [bcrypt](https://github.com/pyca/bcrypt/) - Password hashing library.
- [Python-JOSE](https://python-jose.readthedocs.io/en/latest/) - JWT handling in Python.
- [Bootstrap](https://getbootstrap.com/) - Inspiration for responsive design (if applicable).

---
