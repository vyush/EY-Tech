---
title: Tata Capital AI Loan Assistant
emoji: 🏦
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.49.1"
app_file: app.py
pinned: false
license: mit
short_description: AI-powered loan assistant with agentic architecture
tags:
  - finance
  - loan
  - ai-assistant
  - gradio
  - nbfc
  - fintech
---

# 🏦 Tata Capital - AI Loan Assistant

An advanced **Agentic AI Loan Assistant** for NBFC (Non-Banking Financial Company) with complete loan processing workflow using Master Agent + Worker Agents architecture.

## 🚀 Features

### 🤖 **Agentic AI Architecture**
- **Master Agent**: Orchestrates the entire conversation flow
- **4 Worker Agents**: Sales, Verification, Underwriting, and Sanction Letter Generation
- **Smart Conversation Management**: Context-aware interactions
- **Multi-customer Support**: Both existing and new customers

### 💬 **Interactive Chat Interface**
- **Clickable Buttons**: Quick actions for common responses
- **Multiple Loan Types**: Personal, Business, Wedding, Medical, Travel, Education, Home Renovation
- **Real-time Processing**: Instant approval for eligible customers
- **Professional UI**: Bank-grade interface with Gradio

### 🎯 **Loan Processing Capabilities**
- **Instant Eligibility Assessment**: AI-powered credit evaluation
- **Dynamic Interest Rates**: Based on loan type and customer profile
- **Flexible EMI Options**: 12-60 months tenure
- **KYC Verification**: Digital document processing
- **PDF Generation**: Professional sanction letters

### 📊 **Analytics Dashboard**
- **Real-time Statistics**: Application metrics and approval rates
- **Customer Database**: Synthetic customer management
- **Application History**: Complete loan application tracking
- **Performance Metrics**: Success rates and trends

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Google Gemini API Key (optional for AI responses)

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EY-Tech-yg1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   python loan_agent_complete.py
   ```

5. **Access the interface**
   - Open browser: `http://127.0.0.1:7861`

## 🏗️ Architecture

### Master Agent (Orchestrator)
- Manages conversation flow across multiple stages
- Coordinates all worker agents
- Maintains context and state management
- Handles both existing and new customer journeys

### Worker Agents

#### 1. 🎯 Sales Agent
- Pitches loan products with personalized offers
- Negotiates terms (amount, tenure, interest rates)
- Handles customer objections persuasively
- Creates urgency and value propositions

#### 2. ✅ Verification Agent
- Validates KYC from CRM database
- Verifies customer identity and documents
- Handles both existing and new customer verification
- Manages digital KYC process

#### 3. 📊 Underwriting Agent
- Fetches credit scores from bureau APIs
- Assesses loan eligibility using multiple criteria:
  - **Instant Approval**: Amount ≤ pre-approved limit
  - **Conditional Approval**: Amount ≤ 2× limit & EMI ≤ 50% salary
  - **Rejection**: Credit score < 700 or amount > 2× limit
- Calculates risk and confidence scores

#### 4. 📄 Sanction Letter Generator
- Creates professional PDF sanction letters
- Includes all loan details and terms
- Generates unique reference numbers
- Professional formatting with company branding

## 💼 Loan Types Supported

| Loan Type | Interest Rate | Special Features |
|-----------|---------------|------------------|
| **Personal Loan** | 10.99% - 11.5% | No restrictions, flexible use |
| **Business Loan** | 11.5% | Up to ₹1 crore, no collateral |
| **Wedding Loan** | 10.99% + 0.5% discount | Wedding planning consultation |
| **Home Renovation** | 10.5% - 11.0% | Vendor tie-ups, specialist support |
| **Travel Loan** | 10.99% | Partner discounts, travel insurance |
| **Medical Loan** | 9.99% - 10.5% | Emergency approval, hospital tie-ups |
| **Education Loan** | 10.25% - 10.75% | Moratorium period, tax benefits |

## 🎮 User Interface

### Interactive Elements
- **🚀 Quick Actions**: Start Application, Existing/New Customer
- **💰 Loan Types**: Direct loan type selection buttons
- **💼 Quick Salary**: Common salary range buttons
- **💸 Quick Amounts**: Popular loan amount buttons
- **⚡ Quick Responses**: Yes/No/Proceed/Help buttons

### Navigation Flow
```
Welcome → Name Collection → Loan Type Selection → 
Information Gathering → Offer Generation → Terms Agreement → 
Verification → Approval Decision → Documentation
```

## 📁 File Structure

```
EY-Tech-yg1/
├── loan_agent_complete.py    # Main application with all features
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore rules
├── .env.example            # Environment variables template
├── .env                    # Environment variables (excluded)
├── loan_applications.csv   # Application data (excluded)
├── conversation_logs.json  # Chat logs (excluded)
└── *.pdf                   # Generated sanction letters (excluded)
```

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_google_gemini_api_key
```

### Customer Database
The system includes 10+ synthetic customers with varying profiles:
- Credit scores: 620-850
- Salary ranges: ₹30k-₹1L+
- Different cities and demographics
- Existing loan relationships

## 📈 Analytics & Reporting

### Available Metrics
- **Total Applications**: Count of all loan applications
- **Approval Rates**: Percentage breakdown by decision type
- **Average Loan Amount**: Mean loan amount requested
- **Credit Score Distribution**: Average credit scores
- **Geographic Analysis**: Applications by city
- **Loan Type Popularity**: Most requested loan categories

### Dashboard Features
- Real-time application statistics
- Customer database viewer
- Application history with filters
- Export capabilities

## 🚀 Advanced Features

### AI Integration
- **Google Gemini**: Fallback conversational AI
- **Context Awareness**: Maintains conversation context
- **Smart Responses**: Handles edge cases intelligently

### Data Management
- **CSV Storage**: Application data persistence
- **JSON Logging**: Conversation history tracking
- **PDF Generation**: Professional document creation
- **Error Handling**: Robust failure management

### Security Features
- **Environment Variables**: Secure API key management
- **Data Validation**: Input sanitization and validation
- **Error Boundaries**: Graceful error handling
- **Audit Trail**: Complete application tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and queries:
- Create an issue in the repository
- Contact the development team
- Check the documentation for common solutions

## 🏆 Acknowledgments

- **EY Tech Challenge**: Original project inspiration
- **Tata Capital**: Business domain and requirements
- **Gradio**: UI framework for rapid prototyping
- **Google Gemini**: AI capabilities integration

---

**Built with ❤️ for the EY Tech Challenge 2025**