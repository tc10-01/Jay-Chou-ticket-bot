# 🤖 AI Writing Assistant

A full-stack MERN (MongoDB, Express.js, React.js, Node.js) application that helps users improve their writing using AI technology.

## 🌟 Features

- **AI-Powered Writing Assistance**
  - Real-time writing suggestions
  - Grammar and style corrections
  - Content enhancement recommendations
  - Tone and voice analysis

- **User-Friendly Interface**
  - Clean and intuitive design
  - Real-time editing
  - Document management
  - History tracking

- **Advanced Features**
  - Multiple language support
  - Custom writing styles
  - Export options
  - Collaborative editing

## 🛠️ Tech Stack

### Frontend
- React.js
- Material-UI
- Redux for state management
- Axios for API calls

### Backend
- Node.js
- Express.js
- MongoDB
- JWT Authentication
- OpenAI API integration

## 🚀 Getting Started

### Prerequisites
- Node.js (v14 or higher)
- MongoDB
- npm or yarn
- OpenAI API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/tc10-01/Ai-Wriging-Assistant-MERN.git
cd Ai-Wriging-Assistant-MERN
```

2. Install dependencies for both client and server
```bash
# Install server dependencies
cd server
npm install

# Install client dependencies
cd ../client
npm install
```

3. Set up environment variables
```bash
# In the server directory, create a .env file
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development servers
```bash
# Start the backend server (from server directory)
npm run dev

# Start the frontend development server (from client directory)
npm start
```

## 📁 Project Structure

```
Ai-Wriging-Assistant-MERN/
├── client/                 # Frontend React application
│   ├── public/            # Public assets
│   │   ├── components/    # React components
│   │   ├── pages/        # Page components
│   │   ├── redux/        # Redux state management
│   │   ├── services/     # API services
│   │   └── utils/        # Utility functions
│   └── package.json
│
└── server/                # Backend Node.js application
    ├── config/           # Configuration files
    ├── controllers/      # Route controllers
    ├── models/          # MongoDB models
    ├── routes/          # API routes
    ├── middleware/      # Custom middleware
    └── package.json
```

## 🔒 Environment Variables

### Server (.env)
```
PORT=5000
MONGODB_URI=your_mongodb_uri
JWT_SECRET=your_jwt_secret
OPENAI_API_KEY=your_openai_api_key
```

### Client (.env)
```
REACT_APP_API_URL=http://localhost:5000/api
```

## 📝 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Writing Assistant
- `POST /api/writing/analyze` - Analyze text
- `POST /api/writing/enhance` - Enhance content
- `GET /api/writing/history` - Get writing history
- `POST /api/writing/save` - Save document

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **tc10-01** - *Initial work* - [tc10-01](https://github.com/tc10-01)

## 🙏 Acknowledgments

- OpenAI for providing the AI capabilities
- Material-UI for the beautiful components
- All contributors who have helped shape this project 