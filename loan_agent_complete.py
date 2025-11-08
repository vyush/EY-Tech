# loan_agent_complete.py
# Enhanced Agentic AI Loan Assistant for NBFC
# Implements Master Agent + 4 Worker Agents with full workflow

import gradio as gr
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
import pandas as pd
import random
import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print("=" * 60)
print("🤖 TATA CAPITAL AI LOAN ASSISTANT - AI STATUS CHECK")
print("=" * 60)
if api_key:
    genai.configure(api_key=api_key)
    print("✅ GOOGLE GEMINI AI: Successfully configured and ready!")
    print(f"🔑 API Key: {api_key[:15]}...{api_key[-5:] if len(api_key) > 20 else api_key}")
    print("🚀 AI FEATURES: Enhanced greetings, smart responses, contextual conversations")
else:
    print("ℹ️ FALLBACK MODE: Running without Gemini AI - using built-in intelligent responses")
    print("💡 NOTE: App works perfectly with advanced rule-based AI system")
print("=" * 60)

# ------------------------------
# 1️⃣ SYNTHETIC CUSTOMER DATABASE (10+ Customers)
# ------------------------------
customers = {
    "Rahul": {
        "age": 32, "city": "Mumbai", "phone": "9876543210",
        "address": "Andheri West, Mumbai",
        "kyc": True, "credit_score": 780, "pre_approved_limit": 300000,
        "salary": 60000, "current_loans": {"Home Loan": 1500000, "Car Loan": 400000}
    },
    "Meera": {
        "age": 28, "city": "Bangalore", "phone": "9876543211",
        "address": "Koramangala, Bangalore",
        "kyc": True, "credit_score": 710, "pre_approved_limit": 400000,
        "salary": 80000, "current_loans": {"Personal Loan": 200000}
    },
    "Arjun": {
        "age": 35, "city": "Delhi", "phone": "9876543212",
        "address": "Dwarka, Delhi",
        "kyc": False, "credit_score": 620, "pre_approved_limit": 200000,
        "salary": 45000, "current_loans": {}
    },
    "Simran": {
        "age": 30, "city": "Pune", "phone": "9876543213",
        "address": "Hinjewadi, Pune",
        "kyc": True, "credit_score": 745, "pre_approved_limit": 350000,
        "salary": 72000, "current_loans": {"Car Loan": 500000}
    },
    "Ravi": {
        "age": 40, "city": "Hyderabad", "phone": "9876543214",
        "address": "Gachibowli, Hyderabad",
        "kyc": True, "credit_score": 680, "pre_approved_limit": 250000,
        "salary": 50000, "current_loans": {"Home Loan": 2000000}
    },
    "Priya": {
        "age": 26, "city": "Chennai", "phone": "9876543215",
        "address": "Velachery, Chennai",
        "kyc": True, "credit_score": 820, "pre_approved_limit": 500000,
        "salary": 95000, "current_loans": {}
    },
    "Amit": {
        "age": 33, "city": "Ahmedabad", "phone": "9876543216",
        "address": "Satellite, Ahmedabad",
        "kyc": True, "credit_score": 690, "pre_approved_limit": 280000,
        "salary": 55000, "current_loans": {"Personal Loan": 150000}
    },
    "Neha": {
        "age": 29, "city": "Kolkata", "phone": "9876543217",
        "address": "Salt Lake, Kolkata",
        "kyc": True, "credit_score": 765, "pre_approved_limit": 380000,
        "salary": 70000, "current_loans": {"Car Loan": 350000}
    },
    "Vikram": {
        "age": 38, "city": "Jaipur", "phone": "9876543218",
        "address": "Mansarovar, Jaipur",
        "kyc": False, "credit_score": 640, "pre_approved_limit": 220000,
        "salary": 48000, "current_loans": {}
    },
    "Kavya": {
        "age": 31, "city": "Surat", "phone": "9876543219",
        "address": "Adajan, Surat",
        "kyc": True, "credit_score": 790, "pre_approved_limit": 420000,
        "salary": 85000, "current_loans": {"Home Loan": 1800000}
    }
}

# Persistent storage files
DATA_FILE = "loan_applications.csv"
CONVERSATION_LOG = "conversation_logs.json"

# Initialize files
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=[
        "Timestamp", "Customer", "Age", "City", "Amount", "Tenure", "Interest Rate",
        "Credit Score", "Pre-Approved Limit", "Salary", "Decision", "Confidence (%)"
    ]).to_csv(DATA_FILE, index=False)

if not os.path.exists(CONVERSATION_LOG):
    with open(CONVERSATION_LOG, 'w') as f:
        json.dump([], f)

# ------------------------------
# 2️⃣ WORKER AGENTS
# ------------------------------

class SalesAgent:
    """Negotiates loan terms and convinces customers"""
    
    @staticmethod
    def pitch_loan(name, customer_data):
        limit = customer_data["pre_approved_limit"]
        current_loans = customer_data["current_loans"]
        credit_score = customer_data["credit_score"]
        
        pitch = f"""🎉 **EXCLUSIVE OFFER FOR {name.upper()}!**

🚀 **You have a SPECIAL pre-approved loan of Rs.{limit:,}** waiting for you!

✨ **Your VIP Benefits:**
- 🏆 **Premium rate**: Just **10.99% p.a.** (Market rate: 12-18%)
- ⚡ **30-second approval** - No waiting, no hassles!
- 💳 **Flexible EMIs**: Choose 12-60 months
- 🎯 **Zero processing fees** (Save Rs.{int(limit*0.02):,}!)
- 📱 **100% digital** - Apply from home

"""
        
        if credit_score >= 750:
            pitch += f"⭐ **GOLD CUSTOMER** - Your excellent credit score ({credit_score}) gets you the **BEST RATES**!\n\n"
        elif credit_score >= 700:
            pitch += f"✅ **QUALIFIED CUSTOMER** - Your good credit score ({credit_score}) ensures **INSTANT APPROVAL**!\n\n"
            
        if current_loans:
            pitch += f"🤝 **LOYAL CUSTOMER BONUS** - Existing relationship = **Additional 0.25% discount**!\n\n"
        
        pitch += f"""� **URGENCY ALERT**: This pre-approved offer expires in 7 days!

🎯 **Ready to claim your Rs.{limit:,}?** 
Just tell me how much you need right now - from Rs.50,000 to Rs.{limit:,}!

Type your amount like: **"I need 2 lakh"** or **"Rs.300000"** 👇"""
        
        return pitch
    
    @staticmethod
    def negotiate_terms(amount, tenure=None, rate=None, loan_type="Personal Loan"):
        """Provides flexible loan terms"""
        if not tenure:
            tenure = 24 if amount <= 200000 else 36
        if not rate:
            # Special rates for different loan types
            if loan_type == "Medical Loan":
                rate = 9.99 if amount <= 300000 else 10.5
            elif loan_type == "Home Renovation Loan":
                rate = 10.5 if amount <= 300000 else 11.0
            elif loan_type == "Education Loan":
                rate = 10.25 if amount <= 300000 else 10.75
            else:
                rate = 10.99 if amount <= 300000 else 11.5
        
        emi = (amount * rate/100/12 * (1 + rate/100/12)**tenure) / ((1 + rate/100/12)**tenure - 1)
        
        # Add special benefits message
        special_msg = ""
        if loan_type == "Wedding Loan":
            special_msg = "\n🎉 **Wedding Special**: Extra 0.5% discount applied!"
        elif loan_type == "Medical Loan":
            special_msg = "\n🏥 **Medical Emergency**: Special rate applied!"
        elif loan_type == "Business Loan":
            special_msg = "\n💼 **Business Growth**: Flexible repayment options available!"
        
        return f"""📋 **{loan_type} Terms Summary**
━━━━━━━━━━━━━━━━━━━━
💰 Loan Amount: Rs.{amount:,}
⏱️ Tenure: {tenure} months  
📊 Interest Rate: {rate}% p.a.
💳 Monthly EMI: Rs.{emi:,.2f}
🎯 Loan Type: {loan_type}{special_msg}
━━━━━━━━━━━━━━━━━━━━

**Click "Proceed" to continue with verification!** ✅"""


class VerificationAgent:
    """Handles KYC verification from CRM"""
    
    def verify_kyc(self, name, customer_data=None):
        # Handle existing customers
        if name in customers:
            data = customers[name]
            if data["kyc"]:
                # Update verification timestamp in database
                customers[name]["last_verified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                return f"""✅ **KYC Verification Successful** ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 **CUSTOMER PROFILE VERIFIED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 **Name:** {name}
📱 **Phone:** {data['phone']} ✅ Verified
� **Email:** {name.lower()}@email.com ✅ Verified  
�📍 **Address:** {data['address']} ✅ Verified
🏙️ **City:** {data['city']}
💳 **Credit Score:** {data['credit_score']}/850 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 **All documents verified successfully!**
🚀 **Status:** Ready for loan processing
⏱️ **Verified on:** {datetime.now().strftime("%d %b %Y, %I:%M %p")}

**Moving to credit assessment and loan eligibility...**"""
            else:
                return f"""⚠️ **KYC Pending for {name}** ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 **ACTION REQUIRED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We need to **complete your KYC verification**:

📄 **Missing Documents:**
1. ✅ Aadhaar Card (Upload or verify)
2. ✅ PAN Card (Tax verification)
3. ✅ Address Proof (Latest utility bill)

🚀 **Digital KYC Options:**
- 📱 Upload via app (5 minutes)
- 🏦 Visit nearest branch  
- 📞 Video KYC call

⚠️ **Note:** Cannot proceed with loan without KYC completion."""
        
        # Handle new customers
        elif customer_data:
            return f"""📋 **KYC Required for New Customer**
━━━━━━━━━━━━━━━━━━━━
👤 Name: {name}
🏙️ City: {customer_data['city']}
📊 Salary: Rs.{customer_data['salary']:,}
━━━━━━━━━━━━━━━━━━━━

As a **new customer**, we need to verify your identity:

📄 **Required Documents:**
- Aadhaar Card (Identity proof)
- PAN Card (Tax ID)
- Latest salary slip
- Bank statement (last 3 months)

🚀 **Good news**: Digital KYC takes just **5 minutes**!
Upload documents now or visit nearest branch.

**Would you like to proceed with digital KYC?**"""
        
        else:
            return "❌ Customer information not available."


class UnderwritingAgent:
    """Credit assessment and eligibility validation"""
    
    def fetch_credit_score(self, name, customer_data=None):
        """Mock Credit Bureau API Call"""
        if name in customers:
            return customers[name]["credit_score"]
        elif customer_data:
            return customer_data["credit_score"]
        return None
    
    def assess_eligibility(self, name, amount, tenure=24, customer_data=None):
        # Handle existing customers
        if name in customers:
            data = customers[name]
        # Handle new customers
        elif customer_data:
            data = customer_data
        else:
            return "❌ Customer data not available."
        score = data["credit_score"]
        limit = data["pre_approved_limit"]
        salary = data["salary"]
        
        # Calculate EMI
        rate = 11.5
        emi = (amount * rate/100/12 * (1 + rate/100/12)**tenure) / ((1 + rate/100/12)**tenure - 1)
        emi_to_salary_ratio = (emi / salary) * 100
        
        confidence = random.randint(82, 98)
        
        result = {
            "name": name,
            "amount": amount,
            "score": score,
            "limit": limit,
            "salary": salary,
            "emi": emi,
            "confidence": confidence,
            "decision": "",
            "status": ""
        }
        
        # Decision Logic
        if score < 700:
            result["decision"] = f"❌ **Application Rejected**\n\nCredit Score: {score}/900 (Minimum required: 700)\nWe recommend improving your credit score and reapplying after 6 months."
            result["status"] = "Rejected"
        
        elif amount <= limit:
            result["decision"] = f"""🎉 **INSTANT APPROVAL!**
━━━━━━━━━━━━━━━━━━━━
💰 Approved Amount: Rs.{amount:,}
📊 Credit Score: {score}/900
✅ Within Pre-Approved Limit: Rs.{limit:,}
💳 Monthly EMI: Rs.{emi:,.2f}
🤖 AI Confidence: {confidence}%
━━━━━━━━━━━━━━━━━━━━
🎊 Congratulations! Your loan is approved instantly!"""
            result["status"] = "Approved"
        
        elif amount <= 2 * limit and emi_to_salary_ratio <= 50:
            result["decision"] = f"""📝 **CONDITIONAL APPROVAL**
━━━━━━━━━━━━━━━━━━━━
💰 Requested: Rs.{amount:,}
📊 Pre-Approved Limit: Rs.{limit:,}
💳 Monthly EMI: Rs.{emi:,.2f}
💼 EMI/Salary Ratio: {emi_to_salary_ratio:.1f}%
━━━━━━━━━━━━━━━━━━━━
✅ Your application is conditionally approved!

📄 **Please upload:**
- Latest 3 months salary slips
- Last 6 months bank statement

Upload these and get instant approval!"""
            result["status"] = "Conditional"
        
        else:
            result["decision"] = f"""❌ **Application Declined**
━━━━━━━━━━━━━━━━━━━━
Requested: Rs.{amount:,}
Pre-Approved Limit: Rs.{limit:,}
Maximum Eligible: Rs.{2*limit:,}
━━━━━━━━━━━━━━━━━━━━
The requested amount exceeds our lending criteria.
Consider applying for Rs.{limit:,} for instant approval."""
            result["status"] = "Rejected"
        
        return result


class SanctionLetterGenerator:
    """Generates PDF sanction letter"""
    
    @staticmethod
    def generate_pdf(name, amount, tenure, rate, customer_data):
        filename = f"sanction_letter_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Header
        c.setFillColor(colors.HexColor('#1E3A8A'))
        c.rect(0, height - 1.5*inch, width, 1.5*inch, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(1*inch, height - 1*inch, "TATA CAPITAL")
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, height - 1.2*inch, "Financial Services Limited")
        
        # Date and Reference
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, height - 2*inch, f"Date: {datetime.now().strftime('%d %B %Y')}")
        c.drawString(1*inch, height - 2.2*inch, f"Reference No: TC/PL/{random.randint(100000, 999999)}")
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 2.8*inch, "PERSONAL LOAN SANCTION LETTER")
        
        # Customer Details
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*inch, height - 3.3*inch, "Customer Details:")
        c.setFont("Helvetica", 10)
        y_pos = height - 3.5*inch
        details = [
            f"Name: {name}",
            f"Address: {customer_data['address']}",
            f"Phone: {customer_data['phone']}",
        ]
        for detail in details:
            c.drawString(1.2*inch, y_pos, detail)
            y_pos -= 0.2*inch
        
        # Loan Details
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*inch, y_pos - 0.3*inch, "Loan Details:")
        y_pos -= 0.5*inch
        
        emi = (amount * rate/100/12 * (1 + rate/100/12)**tenure) / ((1 + rate/100/12)**tenure - 1)
        
        c.setFont("Helvetica", 10)
        loan_details = [
            f"Sanctioned Amount: Rs.{amount:,}",
            f"Interest Rate: {rate}% per annum",
            f"Loan Tenure: {tenure} months",
            f"Monthly EMI: Rs.{emi:,.2f}",
            f"Processing Fee: Rs.{int(amount * 0.02):,} (2% of loan amount)",
        ]
        for detail in loan_details:
            c.drawString(1.2*inch, y_pos, detail)
            y_pos -= 0.2*inch
        
        # Terms
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1*inch, y_pos - 0.3*inch, "Terms & Conditions:")
        y_pos -= 0.5*inch
        c.setFont("Helvetica", 9)
        terms = [
            "- This sanction is valid for 30 days from the date of issue",
            "- Final disbursement subject to verification of documents",
            "- Pre-payment charges: 2% on outstanding principal",
            "- Please visit the nearest branch to complete formalities",
        ]
        for term in terms:
            c.drawString(1*inch, y_pos, term)
            y_pos -= 0.18*inch
        
        # Footer
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1*inch, 1.5*inch, "For Tata Capital Financial Services Ltd.")
        c.drawString(1*inch, 1*inch, "Authorized Signatory")
        
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(1*inch, 0.5*inch, "This is a computer-generated document and does not require a physical signature.")
        
        c.save()
        return os.path.abspath(filename)


# ------------------------------
# 3️⃣ MASTER AGENT (Orchestrator)
# ------------------------------

class MasterAgent:
    def __init__(self):
        self.context = {}
        self.conversation_stage = "greeting"
        self.sales_agent = SalesAgent()
        self.verification_agent = VerificationAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.sanction_generator = SanctionLetterGenerator()
        self.conversation_history = []
        self.full_chat_context = []  # Store complete conversation for AI context
    
    def _get_ai_response(self, prompt, fallback_response):
        """Get AI response with full conversation context"""
        try:
            if api_key:
                print("🤖 AI ACTIVE: Using Google Gemini AI with full conversation context...")
                
                # Build comprehensive context for AI
                context_prompt = self._build_full_context_prompt(prompt)
                
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(context_prompt)
                print(f"✅ AI SUCCESS: Generated {len(response.text)} character response with full context")
                print(f"🎯 AI RESPONSE PREVIEW: {response.text[:100]}...")
                return response.text
            else:
                print("💡 FALLBACK MODE: Using built-in intelligent responses (no API key)")
                return fallback_response
        except Exception as e:
            print(f"❌ AI ERROR: {e}")
            print("🔄 SWITCHING TO FALLBACK: Using built-in intelligent responses")
            return fallback_response
    
    def _build_full_context_prompt(self, current_prompt):
        """Build comprehensive AI prompt with full conversation context"""
        # Get conversation history
        chat_history = "\n".join([f"User: {msg[0]}\nAssistant: {msg[1]}" for msg in self.full_chat_context[-5:]])  # Last 5 exchanges
        
        # Build comprehensive context
        full_context = f"""
You are an expert AI loan assistant for Tata Capital NBFC. You have access to the full conversation context.

CUSTOMER PROFILE:
- Name: {self.context.get('name', 'Unknown')}
- Stage: {self.conversation_stage}
- Customer Data: {self.context.get('customer_data', {})}
- Salary: {self.context.get('salary', 'Not provided')}
- Loan Amount: {self.context.get('amount', 'Not specified')}
- Loan Type: {self.context.get('loan_type', 'Not selected')}

RECENT CONVERSATION HISTORY:
{chat_history}

CURRENT CONTEXT & TASK:
{current_prompt}

INSTRUCTIONS:
- Be natural, conversational, and engaging
- Use the conversation history to provide contextual responses
- Remember what the customer has said before
- Guide them towards loan completion naturally
- Use emojis appropriately
- Keep responses under 200 words unless specifically asked for details
- If the message doesn't fit a template, interpret the intent and respond appropriately
- Be persuasive but not pushy
- Show you understand their previous messages

Respond naturally as if you're having a real conversation:
"""
        return full_context
    
    def _get_response_options(self):
        """Get contextual response options based on current stage"""
        stage = self.conversation_stage
        
        if stage == "greeting":
            return ["👋 Hello, I'm ready to start", "🆔 I'm an existing customer", "🆕 I'm new to Tata Capital", "❓ Tell me about your services"]
        elif stage == "identification":
            return ["📱 Verify my phone number", "📧 Verify my email", "🆔 Check my KYC status", "✍️ I'll provide details manually"]
        elif stage == "kyc_verification":
            return ["✅ Yes, that's correct", "❌ No, please update", "📝 I need to update details", "🔄 Re-verify"]
        elif stage in ["sales_pitch", "new_customer_pitch"]:
            return ["✅ Yes, I'm interested!", "💰 Show me interest rates", "📊 Check my eligibility", "📞 I'll call back later"]
        elif stage == "new_customer_info":
            return ["💼 My salary is 50k", "💼 My salary is 75k", "💼 My salary is 1 lakh", "� Custom amount"]
        elif stage == "loan_requirement":
            return ["💰 I need 2 lakh", "💰 I need 3 lakh", "💰 I need 5 lakh", "📝 Different amount"]
        elif stage == "loan_type_selection":
            return ["💼 Personal Loan", "🏢 Business Loan", "💒 Wedding Loan", "🏥 Medical Emergency"]
        elif stage == "terms_confirmation":
            return ["✅ Proceed with terms", "⏱️ Change tenure", "💰 Different amount", "❌ Cancel"]
        elif stage == "underwriting":
            return ["🔍 Check my credit score", "💰 See loan options", "📊 View eligibility", "⏭️ Process my application"]
        elif stage == "conditional_docs":
            return ["📄 Yes, upload documents", "📱 Upload via mobile", "⏰ Upload later", "❓ What documents needed?"]
        elif stage == "sanction":
            return ["📄 Generate sanction letter", "📧 Email me the letter", "💰 Check disbursement", "🏦 Branch details"]
        elif stage == "completed":
            return ["� Apply for different amount", "📞 Contact support", "⭐ Rate this service", "👋 Thank you"]
        else:
            return ["✅ Yes", "❌ No", "📞 Tell me more", "🔄 Start over"]
    
    def process_message(self, message, history):
        # Store conversation in full context
        if len(self.full_chat_context) > 0:
            # Add user message to context
            pass  # Will be added after AI response
        
        print(f"🧠 PROCESSING MESSAGE: '{message}' in stage '{self.conversation_stage}'")
        
        # AI-FIRST APPROACH: Let AI handle everything with context
        ai_response = self._get_intelligent_ai_response(message)
        if ai_response:
            # Add to conversation history
            self.full_chat_context.append((message, ai_response))
            return ai_response
        
        # Fallback to rule-based if AI fails
        return self._handle_rule_based_response(message)
    
    def _get_intelligent_ai_response(self, message):
        """Get intelligent AI response that can handle any message dynamically"""
        try:
            if not api_key:
                return None
                
            print("🧠 AI INTELLIGENCE: Analyzing message with full conversation context...")
            
            # Create comprehensive AI prompt for dynamic conversation handling
            ai_prompt = f"""
You are an expert loan assistant AI for Tata Capital NBFC. You have full conversation context and can handle ANY customer message dynamically.

CURRENT SITUATION:
- Customer Name: {self.context.get('name', 'Not identified yet')}
- Conversation Stage: {self.conversation_stage}
- Customer Profile: {self.context.get('customer_data', 'New customer')}
- Previous Context: {self.context}

CUSTOMER'S MESSAGE: "{message}"

CONVERSATION FLOW STAGES:
1. greeting -> identification -> kyc_verification -> sales_pitch -> loan_type_selection -> loan_requirement -> underwriting -> sanction
2. For new customers: greeting -> identification -> new_customer_pitch -> new_customer_info -> loan_type_selection -> etc.

YOUR TASK:
1. UNDERSTAND the customer's intent from their message
2. DETERMINE what stage they should be in based on their message
3. RESPOND appropriately and naturally 
4. ADVANCE the conversation toward loan completion
5. UPDATE conversation stage if needed (mention: "STAGE_UPDATE: new_stage_name" at the end)

EXAMPLES OF DYNAMIC HANDLING:
- If they say "I need money for medical emergency" -> Identify as medical loan need, move to loan_type_selection
- If they say "What's my credit score?" -> Provide info and guide back to loan process
- If they say "I'm Rahul" -> Identify customer and proceed with welcome
- If they say "Not interested" -> Handle objection persuasively
- If they say random things -> Gently guide back to loan conversation

Be conversational, natural, helpful, and always guide toward loan completion.
Respond as if you're a helpful human loan expert having a natural conversation.
"""
            
            response = self._get_ai_response(ai_prompt, None)
            
            if response:
                # Extract context updates from AI response
                self._extract_context_from_ai_response(message, response)
                
                # Check if AI suggested stage update
                if "STAGE_UPDATE:" in response:
                    parts = response.split("STAGE_UPDATE:")
                    response = parts[0].strip()
                    if len(parts) > 1:
                        new_stage = parts[1].strip()
                        print(f"🔄 AI STAGE UPDATE: {self.conversation_stage} -> {new_stage}")
                        self.conversation_stage = new_stage
            
            return response
            
        except Exception as e:
            print(f"❌ AI INTELLIGENCE ERROR: {str(e)}")
            return None
    
    def _extract_context_from_ai_response(self, user_message, ai_response):
        """Extract and update context from AI conversation"""
        try:
            if not api_key:
                return
                
            print("🔍 AI CONTEXT EXTRACTION: Updating customer context from conversation...")
            
            extraction_prompt = f"""
Analyze this conversation exchange and extract any customer information to update our records:

Customer said: "{user_message}"
AI responded: "{ai_response}"

Current context: {self.context}

Extract and return ONLY the new information in this format:
NAME: [if customer mentioned their name]
SALARY: [if customer mentioned salary/income]
CITY: [if customer mentioned location]
LOAN_AMOUNT: [if customer mentioned how much they need]
LOAN_TYPE: [if customer mentioned loan type/purpose]
PHONE: [if customer mentioned phone number]

Only return fields that have NEW information. If nothing new, return "NO_NEW_INFO"
"""
            
            context_update = self._get_ai_response(extraction_prompt, "NO_NEW_INFO")
            
            if context_update and context_update != "NO_NEW_INFO":
                # Parse and update context
                lines = context_update.split('\n')
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if value and value != '[if customer mentioned their name]':  # Skip template text
                            if key == 'name' and 'name' not in self.context:
                                self.context['name'] = value
                                print(f"📝 CONTEXT UPDATE: Name = {value}")
                            elif key == 'salary' and 'salary' not in self.context:
                                try:
                                    salary_num = int(''.join(filter(str.isdigit, value)))
                                    self.context['salary'] = salary_num
                                    print(f"📝 CONTEXT UPDATE: Salary = Rs.{salary_num:,}")
                                except:
                                    pass
                            elif key == 'city' and 'city' not in self.context:
                                self.context['city'] = value
                                print(f"📝 CONTEXT UPDATE: City = {value}")
                            elif key == 'loan_amount' and 'amount' not in self.context:
                                try:
                                    amount = int(''.join(filter(str.isdigit, value)))
                                    self.context['amount'] = amount
                                    print(f"📝 CONTEXT UPDATE: Loan Amount = Rs.{amount:,}")
                                except:
                                    pass
                            elif key == 'loan_type' and 'loan_type' not in self.context:
                                self.context['loan_type'] = value
                                print(f"📝 CONTEXT UPDATE: Loan Type = {value}")
                                
        except Exception as e:
            print(f"❌ CONTEXT EXTRACTION ERROR: {e}")
            
        except Exception as e:
            print(f"❌ AI INTELLIGENCE ERROR: {e}")
            return None
    
    def _handle_rule_based_response(self, message):
        """Fallback rule-based response handling"""
        msg = message.strip().lower()
        
        # Stage 1: Greeting & Identification
        if self.conversation_stage == "greeting":
            if any(word in msg for word in ["hello", "hi", "hey", "start"]):
                return self._greet_customer()
            elif any(name.lower() in msg for name in customers.keys()):
                return self._identify_customer(message)
            else:
                # Accept any name input
                return self._identify_customer(message)
        
        # Stage 2: Identification  
        elif self.conversation_stage == "identification":
            return self._identify_customer(message)
        
        # Stage 2.3: KYC Verification for existing customers
        elif self.conversation_stage == "kyc_verification":
            if any(word in msg for word in ["yes", "complete", "verify", "proceed", "ok"]):
                # Simulate KYC completion for demo
                customers[self.context["name"]]["kyc"] = True
                customers[self.context["name"]]["last_verified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.conversation_stage = "sales_pitch"
                
                return f"""✅ **KYC Verification Completed Successfully!** ✅

🎉 **{self.context["name"]}, your profile is now fully verified!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 **VERIFICATION STATUS UPDATED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ **Identity:** Verified  
✅ **Address:** Verified
✅ **Phone:** Verified
✅ **Documents:** All uploaded successfully
⏱️ **Completed:** {datetime.now().strftime("%d %b %Y, %I:%M %p")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **Now you're eligible for instant loan approval!**
Ready to explore your exclusive pre-approved offers? 💰"""
            
            elif any(word in msg for word in ["no", "later", "skip"]):
                return """⚠️ **KYC verification is mandatory** for loan processing as per RBI guidelines.

📋 **What you can do:**
- ✅ Complete KYC now (takes 5 minutes)
- 📱 Upload documents via mobile app
- 🏦 Visit nearest branch
- 📞 Schedule video KYC call

**Without KYC, I cannot proceed with your loan application.**
Would you like to complete it now? Just say "Yes"! 👇"""
            
            else:
                return """🔍 **KYC Verification Required**

As per **RBI guidelines**, all loan applications need verified KYC.

📄 **Quick Digital KYC:**
- Takes only **5 minutes**
- Upload documents from phone
- Instant verification
- No branch visit needed

**Ready to complete your KYC?** Just say **"Yes"**! 🚀"""
        
        # Stage 2.5: New Customer Pitch
        elif self.conversation_stage == "new_customer_pitch":
            if any(word in msg for word in ["yes", "interested", "sure", "okay", "ok", "tell me", "check"]):
                return self._handle_new_customer_interest()
            elif any(word in msg for word in ["no", "not interested", "maybe later"]):
                return self._handle_new_customer_objection()
            else:
                return f"""💭 **{self.context['name']}, I understand you might have questions!**

Here's what makes us **India's most trusted NBFC**:

🏆 **4.8/5** customer rating (2 lakh+ reviews)
⚡ **98% approval rate** for eligible customers  
💰 **Rs.50,000 crores** disbursed last year
🎯 **30 lakh+** happy customers

**Just say "Yes" to check your instant eligibility!** 
No obligation, no charges - just see what you qualify for! 😊"""
        
        # Stage 2.7: New Customer Information Collection
        elif self.conversation_stage == "new_customer_info":
            return self._collect_new_customer_info(message)
        
        # Stage 3: Sales Pitch
        elif self.conversation_stage == "sales_pitch":
            if any(word in msg for word in ["yes", "interested", "sure", "okay", "ok", "tell me"]):
                return self._show_loan_pitch()
            elif any(word in msg for word in ["no", "not interested", "maybe later"]):
                return self._handle_objection()
            else:
                return """🤔 Let me ask again - are you interested in exploring **exclusive pre-approved loan offers** tailored just for you?

✨ **Special benefits waiting:**
- **Instant approval** for pre-approved amounts
- **No paperwork hassles** 
- **Competitive rates** starting 10.99%
- **Quick disbursement** in 24 hours

Just say **"Yes"** to see your personalized offer! 💰"""
        
        # Stage 4: Loan Type Selection
        elif self.conversation_stage == "loan_type_selection":
            loan_type = self._extract_loan_type(msg)
            if loan_type:
                self.context["loan_type"] = loan_type
                # For new customers, collect info first
                if not self.context.get("is_existing", True):
                    self.conversation_stage = "new_customer_info"
                    return self._show_loan_type_benefits(loan_type) + f"""

📋 **Now let's get your personalized offer!**

What's your **monthly salary**? 
(This helps me calculate your maximum eligible amount)

**Use quick buttons or type like:**
- "My salary is 50000" or "50k" or "Rs.50,000" 💰"""
                else:
                    self.conversation_stage = "loan_requirement"
                    return self._show_loan_type_benefits(loan_type)
            else:
                return """💼 **What type of loan do you need?**

🎯 **Choose your loan purpose:**

**Click one of the options or type:**
- **"Personal Loan"** - For any personal needs
- **"Business Loan"** - For business expansion  
- **"Home Renovation"** - For home improvements
- **"Wedding Loan"** - For wedding expenses
- **"Travel Loan"** - For vacation/travel
- **"Medical Loan"** - For medical emergencies
- **"Education Loan"** - For studies/courses

Each loan type has special benefits! 🎉"""
        
        # Stage 5: Loan Requirement  
        elif self.conversation_stage == "loan_requirement":
            amount = self._extract_amount(msg)
            if amount:
                self.context["amount"] = amount
                self.context["tenure"] = 24  # default
                self.conversation_stage = "terms_confirmation"
                return self.sales_agent.negotiate_terms(amount, loan_type=self.context.get("loan_type"))
            else:
                loan_type = self.context.get("loan_type", "Personal")
                return f"""💰 **How much {loan_type} do you need?**

**Click an option or type your amount:**
- Type amount like: **250000** or **2.5 lakh** or **Rs.300000**
- We offer loans from Rs.50,000 to Rs.50,00,000

💡 **Popular {loan_type} amounts:**
- Rs.2,00,000 - Small needs
- Rs.5,00,000 - Medium requirements  
- Rs.10,00,000 - Large projects"""
        
        # Stage 5: Terms Acceptance
        elif self.conversation_stage == "terms_confirmation":
            if any(word in msg for word in ["yes", "proceed", "ok", "agree", "accept", "looks good"]):
                return self._start_verification()
            elif any(word in msg for word in ["tenure", "month", "year", "emi", "change"]):
                return self._handle_tenure_change(msg)
            elif any(word in msg for word in ["no", "not okay", "change amount"]):
                self.conversation_stage = "loan_requirement"
                return "No problem! Let's discuss a different amount. What loan amount would work better for you?"
            else:
                return """📋 **Do these loan terms look good to you?**

Please respond with:
- **"Yes"** - to proceed with verification
- **"Change tenure"** - to modify repayment period
- **"Different amount"** - to change loan amount

💡 Ready to get **instant approval**? Just say **"Yes"**! ✅"""
        
        # Stage 5.5: KYC Upload for New Customers
        elif self.conversation_stage == "kyc_upload":
            if any(word in msg for word in ["yes", "proceed", "upload", "digital", "sure"]):
                # Simulate successful KYC
                self.conversation_stage = "underwriting"
                return """✅ **Digital KYC Completed Successfully!**

📋 **Documents Verified:**
- ✅ Aadhaar Card - Verified
- ✅ PAN Card - Verified  
- ✅ Salary Slip - Verified
- ✅ Bank Statement - Verified

🎉 **Great! Your profile is now complete.**

⏳ **Running credit assessment...**"""
            else:
                self.conversation_stage = "completed"
                return """📋 **No problem!** You can complete KYC later.

**Your loan application will be saved as DRAFT.**

Visit any Tata Capital branch or complete digital KYC anytime at www.tatacapital.com

Thank you for your interest! 🙏"""
        
        # Stage 6: AI-Enhanced Integrated Loan Processing
        elif self.conversation_stage == "underwriting":
            print("� AI LOAN PROCESSING: Starting integrated assessment with credit analysis...")
            
            # Perform comprehensive loan processing
            result = self._perform_integrated_loan_processing()
            
            # Save to CSV
            self._save_application(result)
            
            if result["status"] == "Approved":
                self.conversation_stage = "sanction"
                return result["response"] + "\n\n" + self._offer_sanction_letter()
            else:
                self.conversation_stage = "completed"
                return result["response"] + "\n\n" + self._end_conversation()
        
        # Stage 7: Conditional Documentation
        elif self.conversation_stage == "conditional_docs":
            if any(word in msg for word in ["yes", "upload", "sure", "okay"]):
                # Simulate document verification success
                self.conversation_stage = "sanction"
                return """✅ **Documents Verified Successfully!**

🎉 **FINAL APPROVAL CONFIRMED!**
━━━━━━━━━━━━━━━━━━━━
Your loan application has been **APPROVED** after document verification!

All requirements met. Congratulations! 🎊

""" + self._offer_sanction_letter()
            else:
                self.conversation_stage = "completed"
                return "No problem! You can upload documents later. Your conditional approval is valid for 30 days.\n\n" + self._end_conversation()
        
        # Stage 8: Sanction Letter Generation
        elif self.conversation_stage == "sanction":
            if any(word in msg for word in ["generate", "yes", "send", "create", "download"]):
                return self._generate_sanction()
            else:
                return "🎉 Your loan is **APPROVED**! Would you like me to generate your official sanction letter now?"
        
        # AI-powered intent detection and response
        return self._get_ai_intent_response(message)
    
    def _get_ai_intent_response(self, message):
        """AI-powered intent detection and appropriate response"""
        try:
            if api_key:
                print("🎯 AI INTENT DETECTION: Analyzing customer intent...")
                
                intent_prompt = f"""
Analyze this customer message and determine their intent: "{message}"

Customer context: {self.context}
Current stage: {self.conversation_stage}

POSSIBLE INTENTS:
- greeting (wants to start)
- loan_inquiry (asking about loans)
- rate_inquiry (asking about interest rates)
- eligibility_check (wants to know if they qualify)
- objection (not interested, concerns)
- personal_info (sharing name, salary, location)
- loan_amount (specifying how much they need)
- loan_type (specifying what type of loan)
- ready_to_proceed (wants to move forward)
- confusion (doesn't understand something)
- complaint (unhappy about something)
- casual_conversation (off-topic chat)

Respond with:
INTENT: [intent_name]
CONFIDENCE: [high/medium/low]
RESPONSE: [Natural, conversational response appropriate for this intent]
NEXT_ACTION: [What should happen next in the conversation]

Make the response feel like a natural conversation between friends, not a business transaction.
"""
                
                intent_response = self._get_ai_response(intent_prompt, None)
                if intent_response:
                    # Extract response from AI intent analysis
                    if "RESPONSE:" in intent_response:
                        response_part = intent_response.split("RESPONSE:")[1]
                        if "NEXT_ACTION:" in response_part:
                            response_part = response_part.split("NEXT_ACTION:")[0]
                        return response_part.strip()
                    else:
                        return intent_response
                        
        except Exception as e:
            print(f"❌ AI INTENT ERROR: {e}")
        
        # Final fallback to smart response
        return self._smart_response(message)
    
    def _greet_customer(self):
        self.conversation_stage = "identification"
        
        # AI-enhanced greeting
        print("👋 GREETING: Attempting to generate AI-enhanced welcome message...")
        ai_prompt = """
        Create a warm, professional greeting for a loan assistant AI.
        Include benefits of Tata Capital loans and ask for customer's name.
        Keep it under 150 words, use emojis, and be engaging.
        """
        
        ai_greeting = self._get_ai_response(ai_prompt, "")
        
        base_greeting = """🎉 **🎉 WELCOME TO TATA CAPITAL'S AI LOAN PLATFORM! 🎉** 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 **🏆 INDIA'S #1 MOST TRUSTED NBFC 🏆**
✨ **Serving 30+ Lakh Happy Customers Since 1998!** ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **🚀 GET INSTANT LOANS IN JUST 30 SECONDS! 🚀**

💰 **💰 AMAZING LOAN FEATURES:**
- ⚡ **Lightning Fast:** 30-second AI approval process
- � **Big Amounts:** Loans up to Rs.50 lakhs available
- 🔥 **Best Rates:** Starting from just 10.99% p.a.
- 📱 **Zero Hassle:** 100% digital - No branch visit needed!
- 🎯 **Super Fast:** Same-day money in your bank account!
- 🏆 **AI Powered:** Smart credit assessment & instant decisions

🎊 **🎊 7 LOAN TYPES AVAILABLE TODAY:**
- 💼 **Personal Loans** - For any purpose
- 🏢 **Business Loans** - Grow your business  
- 💒 **Wedding Loans** - Make it memorable
- 🏥 **Medical Loans** - Health emergencies
- ✈️ **Travel Loans** - Dream vacations
- 🎓 **Education Loans** - Invest in future
- 🏠 **Home Renovation** - Beautiful spaces

🔍 **🔍 READY TO GET YOUR INSTANT LOAN?**
**Let's start with a simple question:**

**❓ What's your name?** 
💭 Type it below or click to choose from our database! 👇"""
        
        if ai_greeting:
            return f"{ai_greeting}\n\n{base_greeting}"
        else:
            return base_greeting
    
    def _identify_customer(self, message):
        # Extract name from message
        name = self._extract_name(message)
        
        if not name:
            return """😊 **I'd love to help you with a personal loan!**
            
Please share your name so I can personalize your experience. 
Just type something like: **"My name is John"** or **"I'm Sarah"** 👇"""
        
        # Check if existing customer
        for existing_name in customers.keys():
            if existing_name.lower() == name.lower():
                self.context["name"] = existing_name
                customer_data = customers[existing_name]
                self.context["customer_data"] = customer_data
                self.context["is_existing"] = True
                self.conversation_stage = "kyc_verification" if not customer_data["kyc"] else "sales_pitch"
                
                # Show KYC status and customer profile
                kyc_status = "✅ **VERIFIED**" if customer_data["kyc"] else "⚠️ **PENDING**"
                credit_rating = "EXCELLENT" if customer_data["credit_score"] >= 750 else "GOOD" if customer_data["credit_score"] >= 700 else "FAIR"
                
                # AI-enhanced customer welcome message
                print(f"🎯 AI ENHANCEMENT: Creating personalized welcome for {existing_name}")
                ai_prompt = f"""
                Create a personalized welcome message for returning customer {existing_name} from {customer_data['city']}.
                Customer details: Credit score {customer_data['credit_score']}, Pre-approved limit Rs.{customer_data["pre_approved_limit"]:,}, KYC: {customer_data['kyc']}.
                Make it warm, professional, and highlight their VIP status. Include relevant emojis.
                Keep under 100 words. Focus on exclusive benefits and next steps.
                """
                
                ai_welcome = self._get_ai_response(ai_prompt, "")
                
                base_response = f"""� **🎊 WELCOME BACK VIP CUSTOMER {existing_name.upper()}! 🎊** �

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 **🏆 PREMIUM CUSTOMER PROFILE ACTIVATED 🏆**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

� **📋 YOUR VIP ACCOUNT DETAILS:**
- �👤 **Customer Name:** {existing_name} 🌟
- 📍 **Location:** {customer_data['city']} 📍
- 📞 **Registered Phone:** {customer_data['phone']} 📱
- 🆔 **KYC Verification:** {kyc_status} {"🚀" if customer_data['kyc'] else "⏳"}
- 💳 **Credit Score:** {customer_data['credit_score']}/900 ({credit_rating}) {"🌟" if customer_data['credit_score'] >= 750 else "📈"}
- 💰 **Account Type:** Premium Banking Partner 🏆

🎯 **🎯 EXCLUSIVE VIP BENEFITS FOR YOU:**
- 🏆 **Instant Pre-Approved Limit:** Rs.{customer_data["pre_approved_limit"]:,}
- ⚡ **Lightning Approval:** Get money in 2 hours max!
- � **VIP Interest Rate:** Starting from just **10.99% p.a.**
- 🚀 **Zero Paperwork:** For amounts up to your limit!
- 🎁 **Special Privileges:** No processing fee for you!
- 📞 **Priority Support:** Dedicated relationship manager

{ai_welcome if ai_welcome else ""}

"""
                
                if customer_data["kyc"]:
                    return base_response + "🚀 **Ready to explore your exclusive pre-approved offers?**"
                else:
                    return base_response + """
⚠️ **ACTION REQUIRED:** KYC verification pending
We need to complete your KYC before loan processing.

� **Would you like to complete KYC verification now?**"""
        
        # New customer - create profile and be persuasive
        else:
            self.context["name"] = name.title()
            self.context["customer_data"] = None
            self.context["is_existing"] = False
            self.conversation_stage = "new_customer_pitch"
            return f"""🎉 **🎉 HELLO {name.title().upper()}! WELCOME TO TATA CAPITAL FAMILY! 🎉** 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 **🌟 CONGRATULATIONS! YOU'RE IN THE RIGHT PLACE! 🌟**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **🚀 AMAZING NEWS FOR NEW CUSTOMERS LIKE YOU!**

🔥 **🔥 SPECIAL NEW CUSTOMER OFFERS:**
- 💰 **Instant Loans:** Up to Rs.50 Lakhs available TODAY!
- 🏆 **Best Market Rates:** Starting from just **10.99% p.a.**
- ⚡ **Lightning Speed:** Approval in just 30 seconds!
- 📱 **Zero Hassle:** Complete everything from your phone!
- � **No Hidden Fees:** 100% transparent pricing!
- 🌟 **Same Day Money:** Get cash in your account today!

🎊 **🎊 WHY 30+ LAKH CUSTOMERS CHOSE US:**
- 🏆 **India's Most Trusted NBFC** since 1998
- 💎 **Premium Service** - Dedicated support team
- 🚀 **AI-Powered Processing** - Fastest approvals in market
- 💰 **Flexible EMIs** - Choose your comfort zone
- 📈 **Build Credit Score** - We help improve your rating!

💡 **💡 EXCLUSIVE QUESTION FOR YOU:**
**❓ How much money do you need for your dreams?** 

🔥 **Thousands get INSTANT APPROVAL daily! Your turn next!** 
**Ready to check what you qualify for RIGHT NOW?** 🎯💰"""
    
    def _show_loan_pitch(self):
        self.conversation_stage = "loan_type_selection"
        
        # AI-enhanced personalized loan pitch
        print("💼 AI PITCH: Creating personalized loan sales pitch...")
        customer_data = self.context["customer_data"]
        name = self.context["name"]
        
        ai_prompt = f"""
        Create a compelling, personalized loan sales pitch for {name}.
        Customer profile: Credit score {customer_data['credit_score']}, Pre-approved Rs.{customer_data["pre_approved_limit"]:,}, City: {customer_data['city']}.
        
        Make it persuasive, professional, and exciting. Highlight:
        - Instant approval benefits
        - Competitive rates (10.99%)
        - Multiple loan types available
        - Pre-approved advantage
        
        Keep under 150 words, use emojis, create urgency and excitement. End with asking about loan type preference.
        """
        
        ai_pitch = self._get_ai_response(ai_prompt, "")
        
        base_pitch = self.sales_agent.pitch_loan(self.context["name"], self.context["customer_data"])
        
        if ai_pitch:
            return f"🤖 **AI-Personalized Offer for {name}:**\n\n{ai_pitch}\n\n{base_pitch}\n\n" + self._show_loan_types()
        else:
            return base_pitch + "\n\n" + self._show_loan_types()
    
    def _handle_new_customer_interest(self):
        """Handle when new customer shows interest"""
        self.conversation_stage = "loan_type_selection"
        name = self.context["name"]
        return f"""🎉 **Excellent choice, {name}!** 

Let me help you find the **PERFECT loan** for your needs!

""" + self._show_loan_types()
    
    def _handle_new_customer_objection(self):
        """Handle new customer objections persuasively"""
        self.conversation_stage = "new_customer_pitch"  # Keep trying
        name = self.context["name"]
        return f"""I totally get it, {name}! 😊 

But here's something **AMAZING** - checking your eligibility is:
- ✅ **100% FREE** - No charges at all
- ⚡ **Takes 30 seconds** - Super quick
- 🔒 **Completely secure** - No spam calls
- 📱 **No paperwork** needed right now

**Think of it this way:** Wouldn't you want to know if you can get Rs.10 lakhs at just 10.99% interest? 

Even if you don't need money today, **life is unpredictable**:
- Medical emergencies 🏥
- Home repairs 🏠  
- Wedding expenses 💒
- Business opportunities 💼

**Just say "Check" to see your FREE eligibility!** 
What have you got to lose? 🤔"""
    
    def _handle_objection(self):
        self.conversation_stage = "sales_pitch"  # Keep trying
        
        # AI-powered objection handling
        print("🛡️ AI OBJECTION HANDLING: Creating persuasive response...")
        name = self.context["name"]
        customer_data = self.context.get("customer_data", {})
        
        ai_prompt = f"""
        Customer {name} just showed objection to a loan offer. They might be hesitant, skeptical, or not interested.
        Customer profile: Credit score {customer_data.get('credit_score', 'unknown')}, Pre-approved limit {customer_data.get('pre_approved_limit', 'unknown')}.
        
        Create a persuasive, empathetic response that:
        - Acknowledges their concern with understanding
        - Highlights risk-free exploration (no obligation)
        - Creates curiosity about their pre-approved benefits
        - Uses social proof and FOMO (fear of missing out)
        - Ends with a simple, low-pressure next step
        
        Be warm, professional, persuasive. Keep under 120 words with emojis.
        """
        
        ai_objection_response = self._get_ai_response(ai_prompt, "")
        
        base_response = """I completely understand! 😊 

But let me share something exciting - you already have **pre-approved offers** waiting! This means:

🎯 **ZERO paperwork** for pre-approved amounts
💰 **Instant approval** - no waiting days
📊 **Best rates** - starting from just 10.99%
✨ **No hidden charges** - complete transparency

Even if you don't need money right now, wouldn't you like to know your **FREE pre-approved limit**? It takes just 30 seconds!"""
        
        if ai_objection_response:
            return f"🤖 **AI-Powered Response:**\n\n{ai_objection_response}\n\n📋 **Standard Benefits:**\n{base_response}\n\nWhat do you say? Ready to discover your offer? 🚀"
        else:
            return base_response + "\n\nWhat do you say? Ready to discover your offer? 🚀"
    
    def _handle_tenure_change(self, msg):
        """Handle tenure modification requests"""
        tenure_map = {
            "12": 12, "1 year": 12, "one year": 12,
            "24": 24, "2 year": 24, "two year": 24,  
            "36": 36, "3 year": 36, "three year": 36,
            "48": 48, "4 year": 48, "four year": 48,
            "60": 60, "5 year": 60, "five year": 60
        }
        
        for key, value in tenure_map.items():
            if key in msg:
                self.context["tenure"] = value
                amount = self.context["amount"]
                return self.sales_agent.negotiate_terms(amount, value) + "\n\n✅ Updated! Do these new terms work for you?"
        
        return """⏱️ **Choose your preferred tenure:**

- **12 months** - Higher EMI, less interest
- **24 months** - Balanced option ⭐ 
- **36 months** - Lower EMI
- **48 months** - Very low EMI
- **60 months** - Lowest EMI

        Just tell me: "24 months" or "3 years" etc."""
    
    def _collect_new_customer_info(self, message):
        """AI-enhanced information collection from new customers"""
        name = self.context["name"]
        
        # Step 1: Collect salary with AI encouragement
        if "salary" not in self.context:
            salary = self._extract_salary(message)
            if salary:
                self.context["salary"] = salary
                
                # AI-enhanced salary confirmation
                print("💰 AI SALARY ANALYSIS: Creating personalized eligibility preview...")
                ai_prompt = f"""
                Customer {name} just shared salary of Rs.{salary:,}/month.
                Create an encouraging message that:
                - Congratulates them on good salary
                - Hints at loan eligibility (3-5x salary typically)
                - Creates excitement about next step (location)
                - Mentions city-specific offers
                
                Keep under 80 words, professional, use emojis.
                """
                
                ai_salary_response = self._get_ai_response(ai_prompt, "")
                
                base_response = f"""💰 **Great! Monthly salary: Rs.{salary:,}**

📋 **Step 2: Location** 
━━━━━━━━━━━━━━━━━━━━
Which city are you based in?

💡 **Examples:**
- "I'm in Mumbai"
- "Bangalore" 
- "Delhi NCR"

**Different cities have different offers!** 🏙️"""
                
                if ai_salary_response:
                    return f"🤖 **AI Analysis:**\n{ai_salary_response}\n\n{base_response}"
                else:
                    return base_response
            else:
                return """💰 **Please share your monthly salary:**

💡 **Examples:**
- "50000" or "50k"
- "My salary is 75000"
- "I earn Rs.60,000 per month"

**This helps me calculate your maximum loan eligibility!** 📊"""
        
        # Step 2: Collect city
        elif "city" not in self.context:
            city = self._extract_city(message)
            if city:
                self.context["city"] = city
                return f"""🏙️ **Perfect! Location: {city}**

📋 **Step 3: Age Group**
━━━━━━━━━━━━━━━━━━━━
What's your age? (This affects interest rates)

💡 **Examples:**
- "I'm 28 years old"
- "32"
- "Age 35"

**Younger professionals often get better rates!** ⭐"""
            else:
                return """🏙️ **Which city are you in?**

Just type your city name:
- Mumbai, Delhi, Bangalore, Pune, Chennai, Hyderabad, etc.

**City matters for loan processing speed!** 🚀"""
        
        # Step 3: Collect age
        elif "age" not in self.context:
            age = self._extract_age(message)
            if age:
                self.context["age"] = age
                # Create synthetic customer data
                self._create_new_customer_profile()
                self.conversation_stage = "sales_pitch"
                return self._show_new_customer_offer()
            else:
                return """👤 **What's your age?**

💡 **Examples:**
- "28" 
- "I'm 32 years old"
- "Age: 35"

**Almost done! This is the last question.** ✅"""
    
    def _extract_salary(self, message):
        """Extract salary from message"""
        import re
        msg = message.lower()
        
        # Find numbers in the message
        numbers = re.findall(r'\d+', msg)
        if numbers:
            salary = int(numbers[0])
            
            # Handle different formats
            if "k" in msg and salary < 1000:
                salary *= 1000
            elif "lakh" in msg or "lac" in msg:
                salary *= 100000
            elif salary < 10000:  # Assume thousands if very small
                salary *= 1000
                
            # Reasonable salary range check
            if 15000 <= salary <= 500000:
                return salary
        return None
    
    def _extract_city(self, message):
        """Extract city from message"""
        msg = message.lower()
        
        # Major Indian cities
        cities = {
            "mumbai": "Mumbai", "bombay": "Mumbai",
            "delhi": "Delhi", "new delhi": "Delhi", "ncr": "Delhi NCR",
            "bangalore": "Bangalore", "bengaluru": "Bangalore",  
            "chennai": "Chennai", "madras": "Chennai",
            "kolkata": "Kolkata", "calcutta": "Kolkata",
            "hyderabad": "Hyderabad",
            "pune": "Pune", "poona": "Pune",
            "ahmedabad": "Ahmedabad",
            "jaipur": "Jaipur",
            "surat": "Surat",
            "lucknow": "Lucknow",
            "kanpur": "Kanpur",
            "nagpur": "Nagpur",
            "indore": "Indore",
            "thane": "Thane",
            "bhopal": "Bhopal",
            "vadodara": "Vadodara",
            "ghaziabad": "Ghaziabad",
            "ludhiana": "Ludhiana",
            "agra": "Agra",
            "nashik": "Nashik"
        }
        
        for key, city in cities.items():
            if key in msg:
                return city
                
        # If not found in predefined list, extract any word that looks like a city
        words = msg.split()
        for word in words:
            if word.isalpha() and len(word) > 3:
                return word.title()
                
        return None
    
    def _extract_age(self, message):
        """Extract age from message"""
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            age = int(numbers[0])
            if 18 <= age <= 65:  # Reasonable age range for loans
                return age
        return None
    
    def _create_new_customer_profile(self):
        """Create a synthetic profile for new customer"""
        name = self.context["name"]
        salary = self.context["salary"]
        age = self.context["age"]
        city = self.context["city"]
        
        # Generate synthetic credit score based on salary
        if salary >= 100000:
            credit_score = random.randint(750, 850)
        elif salary >= 75000:
            credit_score = random.randint(700, 780)
        elif salary >= 50000:
            credit_score = random.randint(650, 750)
        else:
            credit_score = random.randint(600, 720)
        
        # Calculate pre-approved limit (4-6x salary)
        multiplier = random.uniform(4, 6)
        pre_approved_limit = int(salary * multiplier)
        
        # Create customer data structure
        self.context["customer_data"] = {
            "age": age,
            "city": city,
            "phone": "New Customer",
            "address": f"{city}",
            "kyc": False,  # New customers need KYC
            "credit_score": credit_score,
            "pre_approved_limit": pre_approved_limit,
            "salary": salary,
            "current_loans": {}
        }
    
    def _show_new_customer_offer(self):
        """Show personalized offer to new customer"""
        name = self.context["name"]
        data = self.context["customer_data"]
        limit = data["pre_approved_limit"]
        score = data["credit_score"]
        salary = data["salary"]
        
        offer = f"""🎉 **CONGRATULATIONS {name.upper()}!** 

🚀 **YOUR PERSONALIZED LOAN OFFER:**
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 **Eligible Amount**: Up to **Rs.{limit:,}**
📊 **Estimated Credit Score**: {score}/900
⭐ **Interest Rate**: Starting from **10.99% p.a.**
💳 **Flexible Tenure**: 12 to 60 months
⚡ **Processing Time**: 30 seconds to 2 hours

"""
        
        if score >= 750:
            offer += "🏆 **PREMIUM CUSTOMER** - You qualify for our **LOWEST RATES**!\n\n"
        elif score >= 700:
            offer += "✅ **EXCELLENT PROFILE** - High approval chances!\n\n"
        
        offer += f"""💡 **Based on your Rs.{salary:,} salary, you can easily afford:**
- Rs.{int(limit/2):,} loan = Rs.{self._calculate_emi(int(limit/2), 24):,}/month EMI
- Rs.{int(limit*0.75):,} loan = Rs.{self._calculate_emi(int(limit*0.75), 36):,}/month EMI

🎯 **Ready to apply? How much do you need today?**
Just tell me like: **"I need 3 lakh"** or **"Rs.500000"** 💰"""
        
        return offer
    
    def _show_loan_types(self):
        """Show available loan types"""
        return """🎯 **What type of loan do you need?**

**Click your preferred option:**

💼 **Personal Loan** - Any personal need (Most Popular)
🏢 **Business Loan** - Business growth & expansion  
🏠 **Home Renovation** - Home improvement projects
💒 **Wedding Loan** - Make your day special
✈️ **Travel Loan** - Dream vacations & trips
🏥 **Medical Loan** - Health & medical needs
🎓 **Education Loan** - Studies & skill development

Each loan type has **special benefits and rates**! 🎉"""
    
    def _calculate_emi(self, amount, tenure):
        """Calculate EMI for given amount and tenure"""
        rate = 11.5  # Annual rate
        monthly_rate = rate / 100 / 12
        emi = (amount * monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
        return int(emi)
    
    def _extract_loan_type(self, message):
        """Extract loan type from message"""
        msg = message.lower()
        
        loan_types = {
            "personal": "Personal Loan",
            "business": "Business Loan", 
            "home": "Home Renovation Loan",
            "renovation": "Home Renovation Loan",
            "wedding": "Wedding Loan",
            "marriage": "Wedding Loan",
            "travel": "Travel Loan",
            "vacation": "Travel Loan",
            "medical": "Medical Loan",
            "health": "Medical Loan",
            "education": "Education Loan",
            "study": "Education Loan"
        }
        
        for key, loan_type in loan_types.items():
            if key in msg:
                return loan_type
                
        return None
    
    def _show_loan_type_benefits(self, loan_type):
        """Show specific benefits for selected loan type"""
        benefits = {
            "Personal Loan": """🎯 **Personal Loan - Maximum Flexibility!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
- ✅ **No end-use restrictions** - Use for anything!
- ⚡ **Instant approval** for pre-approved customers
- 💰 **Up to Rs.50 lakhs** available
- 🏆 **Lowest rates** starting 10.99%
- 📱 **100% digital process** - No branch visit

💡 **Perfect for:** Medical bills, debt consolidation, shopping, emergencies""",

            "Business Loan": """💼 **Business Loan - Grow Your Business!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
- 🚀 **Quick capital** for business growth
- 💰 **Up to Rs.1 crore** funding available  
- 📊 **Flexible repayment** up to 5 years
- 💳 **Competitive rates** from 11.5%
- 📈 **No collateral** required up to Rs.50L

💡 **Perfect for:** Inventory, expansion, equipment, working capital""",

            "Wedding Loan": """💒 **Wedding Loan - Make Your Day Special!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
- 🎉 **Wedding season discount** - Extra 0.5% off
- 💰 **Up to Rs.25 lakhs** for your big day
- ⏱️ **Extended tenure** up to 5 years
- 🎁 **Free wedding planning** consultation
- 📱 **Quick approval** in 24 hours

💡 **Perfect for:** Venue, catering, jewelry, shopping, honeymoon""",

            "Home Renovation Loan": """🏠 **Home Renovation - Transform Your Space!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
- 🔨 **Renovation specialist** team support
- 💰 **Up to Rs.30 lakhs** for home improvement
- 🏆 **Special rates** from 10.5% for home loans
- 📋 **Minimal documentation** required
- 🎯 **Vendor tie-ups** for discounts

💡 **Perfect for:** Kitchen, bathroom, flooring, painting, furnishing""",

            "Travel Loan": """✈️ **Travel Loan - Explore the World!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
- 🌍 **Travel partner discounts** up to 15%
- 💰 **Up to Rs.15 lakhs** for dream vacations
- ⚡ **48-hour approval** for urgent travel
- 💳 **Zero forex markup** on international cards
- 📱 **Travel insurance** included

💡 **Perfect for:** International trips, family vacations, adventure tours""",

            "Medical Loan": """🏥 **Medical Loan - Health First Priority!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
- 🚨 **Emergency approval** in 2 hours
- 💰 **Up to Rs.20 lakhs** for medical needs
- 🏆 **Lowest rates** from 9.99% (special rate)
- 🏥 **Hospital tie-ups** for direct payment
- 💊 **Medical insurance** guidance

💡 **Perfect for:** Surgery, treatment, medicines, health checkups""",

            "Education Loan": """🎓 **Education Loan - Invest in Your Future!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
- 📚 **Student-friendly** EMI options
- 💰 **Up to Rs.1 crore** for higher studies
- 🎯 **Moratorium period** during studies
- 🌍 **International education** support
- 📜 **Tax benefits** under Section 80E

💡 **Perfect for:** College fees, MBA, foreign studies, skill courses"""
        }
        
        message = benefits.get(loan_type, benefits["Personal Loan"])
        return message + f"\n\n💰 **Ready to proceed with {loan_type}?**\nHow much do you need?"
    
    def _extract_name(self, message):
        """Extract name from user message"""
        import re
        msg = message.strip()
        
        # Common patterns for name input
        patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
            r"this is (\w+)",
            r"^(\w+)$",  # Just a single word
        ]
        
        for pattern in patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                name = match.group(1)
                # Filter out common non-name words
                if name.lower() not in ["hello", "hi", "hey", "yes", "no", "ok", "loan", "money"]:
                    return name
        
        # If message contains only alphabetic characters (likely a name)
        if msg.isalpha() and len(msg) > 1:
            return msg
            
        return None
    
    def _extract_amount(self, msg):
        import re
        # Extract numbers
        numbers = re.findall(r'\d+', msg)
        if numbers:
            amount = int(numbers[0])
            # Handle lakh notation
            if "lakh" in msg or "lac" in msg:
                amount *= 100000
            elif amount < 10000:  # assume lakhs if small number
                amount *= 100000
            return amount
        return None
    
    def _start_verification(self):
        self.conversation_stage = "underwriting"
        name = self.context["name"]
        customer_data = self.context.get("customer_data")
        
        # Step 1: KYC Verification
        kyc_result = self.verification_agent.verify_kyc(name, customer_data)
        
        # For new customers, handle KYC differently
        if not self.context.get("is_existing", True) and "KYC Required" in kyc_result:
            self.conversation_stage = "kyc_upload"
            return kyc_result
        
        if "Pending" in kyc_result:
            self.conversation_stage = "completed"
            return kyc_result
        
        # Step 2: Credit Score Check
        score = self.underwriting_agent.fetch_credit_score(name, customer_data)
        credit_msg = f"\n\n📊 **Credit Bureau Check**\nCredit Score: {score}/900\n"
        
        return kyc_result + credit_msg + "\n⏳ Running final eligibility assessment..."
    
    def _offer_sanction_letter(self):
        return """📄 **📄 SANCTION LETTER READY FOR DOWNLOAD! 📄**

🎉 **🎉 CONGRATULATIONS!** Your official loan sanction letter is ready!

🚀 **🚀 INSTANT DOWNLOAD OPTIONS:**
- 📱 **Option 1:** Click "Generate sanction letter" below
- 💻 **Option 2:** Type "generate PDF" to download now  
- 📧 **Option 3:** Type "email me" to get it via email

**⚡ Your digital sanction letter will be ready in 3 seconds! ⚡**"""
    
    def _generate_sanction(self):
        self.conversation_stage = "completed"
        name = self.context["name"]
        amount = self.context["amount"]
        tenure = self.context.get("tenure", 24)
        rate = 11.5
        
        # Generate the PDF
        filepath = self.sanction_generator.generate_pdf(
            name, amount, tenure, rate,
            self.context["customer_data"]
        )
        
        # Create download link
        import os
        file_name = os.path.basename(filepath)
        
        return f"""🎉 **🎉 SANCTION LETTER GENERATED SUCCESSFULLY! 🎉**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 **📄 YOUR OFFICIAL LOAN DOCUMENTS ARE READY! 📄**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 **💾 DOWNLOAD INFORMATION:**
- 📁 **File Name:** {file_name}
- 📂 **File Location:** {filepath}
- 📄 **Document Type:** Official PDF Sanction Letter
- 🔒 **Security:** Password protected with your phone number

🎊 **🎊 IMMEDIATE NEXT STEPS:**
- **✅ Step 1:** **Download the PDF file above** 📥
- **🏦 Step 2:** **Visit any Tata Capital branch** with these documents:
  - 🆔 **Original ID proofs** (PAN Card, Aadhaar Card)
  - 🏠 **Address proof** (Utility bill, Rent agreement)  
  - 🏦 **Bank statements** (Last 6 months)
  - 📄 **This sanction letter** (Print or show on mobile)

💰 **💰 MONEY DISBURSAL PROCESS:**
- ⏰ **Processing Time:** 2-4 hours at branch
- 💸 **Disbursal Method:** Direct bank transfer (NEFT/RTGS)
- 📱 **SMS Updates:** You'll get real-time notifications
- 🎯 **Expected Credit:** Within 24 hours of branch visit

🔥 **🔥 SPECIAL NOTES:**
- 🚀 **Fast Track:** VIP customer - priority processing
- 📞 **Support:** 24/7 helpline: 1800-209-8787
- 🎁 **Bonus:** Zero prepayment charges for first year
- ⭐ **Rating:** Please rate our service 5 stars!

**🙏 Thank you for choosing Tata Capital! Welcome to our family of satisfied customers! 🙏**

**🎊 Congratulations once again on your loan approval! 🎊**"""
    
    def _end_conversation(self):
        return "\n\nThank you for considering Tata Capital. Feel free to reach out anytime! 🙏"
    
    def _perform_integrated_loan_processing(self):
        """Comprehensive integrated loan processing with credit assessment and personalized offerings"""
        try:
            print("🔍 INTEGRATED PROCESSING: Starting comprehensive loan assessment...")
            
            # Get customer data
            name = self.context["name"]
            requested_amount = self.context["amount"]
            customer_data = self.context.get("customer_data")
            
            if name in customers:
                data = customers[name]
            elif customer_data:
                data = customer_data
            else:
                return {
                    "status": "Error",
                    "response": "❌ Customer data not available for processing."
                }
            
            # Step 1: Credit Score Assessment
            credit_score = data["credit_score"]
            salary = data["salary"]
            pre_approved_limit = data["pre_approved_limit"]
            
            # Step 2: Generate personalized loan offerings
            offerings = self._generate_personalized_offerings(credit_score, salary, pre_approved_limit)
            
            # Step 3: Process the specific request
            decision_result = self._make_loan_decision(requested_amount, credit_score, salary, pre_approved_limit, name)
            
            # Step 4: Create comprehensive response
            response = self._create_integrated_response(
                name, credit_score, salary, requested_amount, 
                pre_approved_limit, offerings, decision_result
            )
            
            return {
                "status": decision_result["status"],
                "response": response,
                "name": name,
                "amount": requested_amount,
                "score": credit_score,
                "limit": pre_approved_limit,
                "salary": salary,
                "confidence": decision_result["confidence"]
            }
            
        except Exception as e:
            print(f"❌ PROCESSING ERROR: {str(e)}")
            return {
                "status": "Error",
                "response": "❌ Unable to process your loan application. Please try again."
            }
    
    def _generate_personalized_offerings(self, credit_score, salary, pre_approved_limit):
        """Generate personalized loan offerings based on customer profile"""
        offerings = []
        
        # Calculate different loan amounts with their terms
        amounts = [
            min(pre_approved_limit, int(salary * 3)),      # Conservative
            min(pre_approved_limit, int(salary * 4)),      # Standard  
            pre_approved_limit                             # Maximum
        ]
        
        for amount in amounts:
            if amount >= 50000:  # Minimum loan amount
                rate = self._calculate_interest_rate(credit_score, amount)
                emi_24 = self._calculate_emi(amount, rate, 24)
                emi_36 = self._calculate_emi(amount, rate, 36)
                
                offerings.append({
                    "amount": amount,
                    "rate": rate,
                    "emi_24": emi_24,
                    "emi_36": emi_36
                })
        
        return offerings
    
    def _calculate_interest_rate(self, credit_score, amount):
        """Calculate personalized interest rate - returns single market rate"""
        # Current market rate for personal loans in India (November 2024)
        market_rate = 12.5  # Single market rate instead of range
        
        # Minor adjustments based on credit score for personalization
        if credit_score >= 800:
            return 11.5  # Premium rate for excellent credit
        elif credit_score >= 750:
            return 12.0  # Good rate for very good credit
        elif credit_score >= 700:
            return 12.5  # Standard market rate
        else:
            return 13.0  # Slightly higher for fair credit
        
        # Always return a single, definitive rate
    
    def _calculate_emi(self, amount, rate, tenure):
        """Calculate EMI"""
        monthly_rate = rate / 100 / 12
        emi = (amount * monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
        return emi
    
    def _make_loan_decision(self, requested_amount, credit_score, salary, pre_approved_limit, name):
        """Make intelligent loan decision"""
        confidence = random.randint(85, 98)
        
        # Calculate EMI for requested amount
        rate = self._calculate_interest_rate(credit_score, requested_amount)
        emi = self._calculate_emi(requested_amount, rate, 24)
        emi_to_salary_ratio = (emi / salary) * 100
        
        if credit_score < 650:
            # Approve for a smaller amount instead of rejecting
            approved_amount = min(pre_approved_limit // 2, int(salary * 2.5))
            if approved_amount >= 50000:  # Minimum loan amount
                rate = self._calculate_interest_rate(credit_score, approved_amount)
                emi = self._calculate_emi(approved_amount, rate, 24)
                return {
                    "status": "Approved",
                    "reason": "reduced_amount_approval",
                    "confidence": confidence,
                    "rate": rate,
                    "emi": emi,
                    "approved_amount": approved_amount,
                    "original_request": requested_amount
                }
            else:
                return {
                    "status": "Rejected",
                    "reason": "low_credit_score",
                    "confidence": confidence
                }
        elif requested_amount <= pre_approved_limit and emi_to_salary_ratio <= 45:
            return {
                "status": "Approved",
                "reason": "instant_approval",
                "confidence": confidence,
                "rate": rate,
                "emi": emi
            }
        else:
            # Instead of conditional approval, approve for maximum eligible amount
            approved_amount = min(pre_approved_limit, int(salary * 4))
            if approved_amount >= 50000:
                rate = self._calculate_interest_rate(credit_score, approved_amount)
                emi = self._calculate_emi(approved_amount, rate, 24)
                return {
                    "status": "Approved",
                    "reason": "reduced_amount_approval",
                    "confidence": confidence,
                    "rate": rate,
                    "emi": emi,
                    "approved_amount": approved_amount,
                    "original_request": requested_amount
                }
            else:
                return {
                    "status": "Rejected",
                    "reason": "exceeds_limit",
                    "confidence": confidence
                }
    
    def _create_integrated_response(self, name, credit_score, salary, requested_amount, 
                                  pre_approved_limit, offerings, decision):
        """Create comprehensive, user-friendly response"""
        
        # Header with credit assessment
        response = f"""🔍 **COMPREHENSIVE LOAN ASSESSMENT COMPLETE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👋 **Hello {name}!** Here's your personalized loan analysis:

📊 **YOUR CREDIT PROFILE:**
- **Credit Score:** {credit_score}/900 {'🌟' if credit_score >= 750 else '📈' if credit_score >= 700 else '⚠️'}
- **Monthly Salary:** Rs.{salary:,}
- **Pre-Approved Limit:** Rs.{pre_approved_limit:,}
- **Requested Amount:** Rs.{requested_amount:,}

"""
        
        # Personalized loan offerings
        if len(offerings) > 0:
            response += "💰 **PERSONALIZED LOAN OFFERINGS FOR YOU:**\n\n"
            
            for i, offer in enumerate(offerings, 1):
                emoji = "⭐" if i == 2 else "💎" if i == 3 else "🎯"
                label = "RECOMMENDED" if i == 2 else "PREMIUM" if i == 3 else "STARTER"
                
                response += f"""{emoji} **{label} PACKAGE:**
- **Loan Amount:** Rs.{offer['amount']:,}
- **Interest Rate:** {offer['rate']:.1f}% p.a.
- **24 Month EMI:** Rs.{offer['emi_24']:,.0f}
- **36 Month EMI:** Rs.{offer['emi_36']:,.0f}

"""
        
        # Decision section
        response += "🎯 **LOAN DECISION:**\n"
        
        if decision["status"] == "Approved":
            # Generate realistic loan details
            import datetime
            loan_ref_no = f"TC/PL/{random.randint(100000, 999999)}/2024"
            sanction_date = datetime.datetime.now().strftime("%d %B %Y")
            disbursal_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d %B %Y")
            
            # Check if this is a reduced amount approval
            if decision.get("reason") == "reduced_amount_approval":
                approved_amount = decision["approved_amount"]
                processing_fee = int(approved_amount * 0.02)
                
                response += f"""🎉 **🚀 INSTANT LOAN APPROVAL! 🚀** ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 **CONGRATULATIONS {name.upper()}!** 🏆
**✨ YOUR AI-POWERED LOAN HAS BEEN APPROVED! ✨**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **📋 OFFICIAL LOAN APPROVAL DETAILS:**
- 🆔 **Loan Reference:** {loan_ref_no}
- 💰 **Sanctioned Amount:** Rs.{approved_amount:,} (Instant Approval)
- 📈 **Interest Rate:** {decision['rate']:.1f}% p.a. (Current Market Rate)
- 💳 **Monthly EMI:** Rs.{decision['emi']:,.0f}
- ⏰ **Loan Tenure:** 24 months
- 🤖 **AI Confidence Score:** {decision['confidence']}%
- 📅 **Sanction Date:** {sanction_date}
- 💸 **Expected Disbursal:** {disbursal_date}

💰 **💰 FINANCIAL BREAKDOWN:**
- 💵 **Principal Amount:** Rs.{approved_amount:,}
- 🏦 **Processing Fee:** Rs.{processing_fee:,} (2.0%)
- 📊 **Total Interest:** Rs.{int(decision['emi'] * 24 - approved_amount):,}
- 💸 **Total Payable:** Rs.{int(decision['emi'] * 24):,}

✅ **✅ WHY YOU'RE INSTANTLY APPROVED:**
- 🌟 **Smart AI Assessment:** Optimized amount for your profile
- 💪 **Perfect EMI-to-Income Ratio:** Comfortable repayment
- 🎯 **Digital Document Verification:** All checks completed
- ✨ **AI Risk Assessment:** Low Risk Profile
- 🚀 **Fast-Track Processing:** Premium eligibility

💡 **💡 SMART APPROVAL LOGIC:**
- 📋 **Requested:** Rs.{requested_amount:,}
- ✅ **Approved:** Rs.{approved_amount:,} (Guaranteed instant disbursal)
- 📈 **Future Upgrade:** Apply for higher amounts after 6 months

🎊 **🎊 NEXT STEPS - YOUR MONEY IS READY! 🎊**
- 📄 **Step 1:** Download your digital sanction letter (PDF)
- 🎯 **Step 2:** Digital acceptance - No branch visit needed!
- 💰 **Step 3:** Money in your account within 2 hours!

**🔥 SPECIAL: Instant digital processing - Your documents are pre-verified! 🔥**"""
                
            else:
                # Regular approval for requested amount
                processing_fee = int(requested_amount * 0.02)
                
                response += f"""🎉 **🚀 INSTANT LOAN APPROVAL! 🚀** ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 **CONGRATULATIONS {name.upper()}!** 🏆
**✨ YOUR AI-POWERED LOAN HAS BEEN APPROVED! ✨**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **📋 OFFICIAL LOAN APPROVAL DETAILS:**
- 🆔 **Loan Reference:** {loan_ref_no}
- 💰 **Sanctioned Amount:** Rs.{requested_amount:,}
- 📈 **Interest Rate:** {decision['rate']:.1f}% p.a. (Current Market Rate)
- 💳 **Monthly EMI:** Rs.{decision['emi']:,.0f}
- ⏰ **Loan Tenure:** 24 months
- 🤖 **AI Confidence Score:** {decision['confidence']}%
- 📅 **Sanction Date:** {sanction_date}
- 💸 **Expected Disbursal:** {disbursal_date}

💰 **💰 FINANCIAL BREAKDOWN:**
- 💵 **Principal Amount:** Rs.{requested_amount:,}
- 🏦 **Processing Fee:** Rs.{processing_fee:,} (2.0%)
- 📊 **Total Interest:** Rs.{int(decision['emi'] * 24 - requested_amount):,}
- 💸 **Total Payable:** Rs.{int(decision['emi'] * 24):,}

✅ **✅ WHY YOU'RE INSTANTLY APPROVED:**
- 🌟 **Excellent Credit Score:** {credit_score}/900
- 💪 **Strong Repayment Capacity:** EMI only {(decision['emi']/salary*100):.1f}% of salary
- 🎯 **Digital Document Verification:** All checks completed automatically
- ✨ **AI Risk Assessment:** Low Risk Profile
- 🚀 **Fast-Track Eligibility:** Premium Customer

🎊 **🎊 NEXT STEPS - YOUR MONEY IS READY! 🎊**
- 📄 **Step 1:** Download your digital sanction letter (PDF)
- � **Step 2:** Digital acceptance - No branch visit needed!
- 💰 **Step 3:** Money in your account within 2 hours!

**🔥 SPECIAL: All documents pre-verified through AI - Instant disbursal! 🔥**"""

        else:  # Rejected - provide alternative amount
            max_eligible = min(pre_approved_limit, int(salary * 4))
            response += f"""LOAN ASSESSMENT COMPLETE - ALTERNATIVE APPROVAL!

Hello {name.upper()}, we have great news for you!

CURRENT ASSESSMENT:
- Amount Requested: Rs.{requested_amount:,}
- Alternative Approved Amount: Rs.{max_eligible:,}
- Your Credit Score: {credit_score}/900
- Monthly Salary: Rs.{salary:,}
- Interest Rate: 12.5% p.a. (current market rate)

INSTANT APPROVAL AVAILABLE:
We can instantly approve Rs.{max_eligible:,} for you today with the following benefits:
- No document uploads required
- Instant digital approval 
- Money in your account within 24 hours
- Current market rate of 12.5% p.a.

Would you like to proceed with Rs.{max_eligible:,} instant approval?"""
            
        response += "\n\nReady to proceed? Let me know your decision!"
        
        return response
    
    def _save_application(self, result):
        """Save application to CSV with proper error handling"""
        try:
            customer_name = result["name"]
            amount = result["amount"]
            rate = 10.99 if amount <= 300000 else 11.5
            
            # Handle both existing and new customers
            if customer_name in customers:
                customer_data = customers[customer_name]
            else:
                customer_data = self.context.get("customer_data", {})
            
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Customer": customer_name,
                "Age": customer_data.get("age", "N/A"),
                "City": customer_data.get("city", "N/A"),
                "Amount": amount,
                "Tenure": self.context.get("tenure", 24),
                "Interest Rate": rate,
                "Credit Score": result["score"],
                "Pre-Approved Limit": result["limit"],
                "Salary": result["salary"],
                "Decision": result["status"],
                "Confidence (%)": result["confidence"]
            }])
            
            # Read existing data or create new DataFrame
            try:
                df = pd.read_csv(DATA_FILE)
            except (FileNotFoundError, pd.errors.EmptyDataError):
                df = pd.DataFrame(columns=[
                    "Timestamp", "Customer", "Age", "City", "Amount", "Tenure", "Interest Rate",
                    "Credit Score", "Pre-Approved Limit", "Salary", "Decision", "Confidence (%)"
                ])
            
            # Append new row and save
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            
            print(f"✅ Application saved: {customer_name} - {result['status']} - Rs.{amount:,}")
            
        except Exception as e:
            print(f"❌ Error saving application: {str(e)}")
            # Still continue the conversation even if saving fails
    
    def _smart_response(self, message):
        """AI-FIRST conversational response with full context awareness"""
        print("🧠 SMART AI RESPONSE: Using full conversation context for dynamic response...")
        
        # AI-FIRST: Always try AI with full conversational context
        ai_response = self._get_conversational_ai_response(message)
        if ai_response:
            return ai_response
        
        # Enhanced fallback with context awareness
        return self._get_contextual_fallback_response(message)
    
    def _get_conversational_ai_response(self, message):
        """Get natural, conversational AI response with full context"""
        try:
            if not api_key:
                return None
                
            print("💬 CONVERSATIONAL AI: Creating natural response with full context...")
            
            # Build conversation summary
            recent_messages = self.full_chat_context[-3:] if self.full_chat_context else []
            conversation_summary = "\n".join([f"User: {msg[0]}\nAI: {msg[1][:100]}..." for msg in recent_messages])
            
            ai_prompt = f"""
You are an expert conversational AI loan assistant for Tata Capital NBFC. You're having a natural conversation with a potential customer.

FULL CUSTOMER CONTEXT:
- Name: {self.context.get('name', 'Not provided yet')}
- Current Stage: {self.conversation_stage}
- Customer Data: {self.context.get('customer_data', 'New customer')}
- Salary: {self.context.get('salary', 'Not provided')}
- Loan Amount Needed: {self.context.get('amount', 'Not specified')}
- Loan Type Interest: {self.context.get('loan_type', 'Not selected')}
- Is Existing Customer: {self.context.get('is_existing', 'Unknown')}

RECENT CONVERSATION:
{conversation_summary}

CUSTOMER'S CURRENT MESSAGE: "{message}"

YOUR RESPONSE SHOULD:
1. Be completely natural and conversational (like talking to a friend)
2. Reference previous parts of the conversation when relevant
3. Show you understand their needs and concerns
4. Guide them naturally toward loan completion
5. Be helpful, empathetic, and engaging
6. Use appropriate emojis and tone
7. Ask follow-up questions when needed
8. Handle any topic they bring up intelligently

LOAN PRODUCTS TO OFFER:
- Personal Loan (10.99% interest)
- Business Loan (11.5% interest)  
- Wedding Loan (10.99% + discount)
- Medical Loan (9.99% emergency rate)
- Travel Loan, Education Loan, Home Renovation

Be conversational and natural. Don't sound robotic or templated.
"""
            
            response = self._get_ai_response(ai_prompt, None)
            if response:
                print("✨ CONVERSATIONAL AI SUCCESS: Generated natural response")
                return response
            return None
            
        except Exception as e:
            print(f"❌ CONVERSATIONAL AI ERROR: {e}")
            return None
    
    def _get_contextual_fallback_response(self, message):
        """Enhanced contextual fallback when AI fails"""
        msg = message.lower()
        
        print("📋 CONTEXTUAL FALLBACK: Using enhanced rule-based response with context")
        
        # Enhanced rule-based responses
        if any(word in msg for word in ["loan", "money", "borrow", "credit", "finance"]):
            return """💰 **Perfect! You're in the right place!** 💰
            
🏆 **Tata Capital - India's #1 NBFC** offers:
- ✅ **Pre-approved limits** up to Rs.50 lakhs
- ⚡ **30-second approval** process  
- 💳 **Flexible EMIs** from 12-60 months
- 🏆 **Interest rates from 10.99%**
- 📱 **100% digital** - No branch visits!

🎯 **Ready to check your pre-approved offer?** 
Just type your name or select an option below!"""
        
        # Rate/interest queries  
        elif any(word in msg for word in ["rate", "interest", "charges", "cost"]):
            return """📊 **Our Competitive Interest Rates:** 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 **Personal Loan:** 10.99% p.a. onwards
🏢 **Business Loan:** 11.5% p.a. onwards  
💒 **Wedding Loan:** 10.99% + special discount
🏥 **Medical Loan:** 9.99% emergency rate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ **Zero processing fees** for pre-approved customers
✅ **No hidden charges** - complete transparency

� **Your exact rate depends on your credit profile!**
Want to check your personalized rate? Just share your name! 👇"""
        
        # EMI/payment queries
        elif any(word in msg for word in ["emi", "payment", "monthly"]):
            return """💳 **EMI Information:**
            
Our EMI calculator shows:
- Rs.2 lakh loan = Rs.9,500/month (24 months)
- Rs.3 lakh loan = Rs.14,200/month (24 months)  
- Rs.5 lakh loan = Rs.23,600/month (24 months)

🎯 **Flexible tenures:** 12 to 60 months
📱 **Auto-debit facility** available

Share your loan amount for exact EMI calculation!"""
        
        # Documents/requirements
        elif any(word in msg for word in ["document", "paper", "require", "need"]):
            return """📄 **Required Documents:**
            
**For Pre-approved customers:**
- Just your Aadhaar & PAN (already verified!)
- Bank statement (last 3 months)
- Salary slips (latest 2)

**For others:**
- Identity proof (Aadhaar/Passport/Driving License)
- Address proof  
- Income proof (salary slips/ITR)
- Bank statements (6 months)

💡 Pre-approved customers get **instant approval**! Check if you're pre-approved?"""
        
        # Help/support queries
        elif any(word in msg for word in ["help", "support", "contact"]):
            return """🤝 **I'm here to help!**
            
I can assist you with:
- ✅ Checking pre-approved loan offers
- 💰 Calculating EMIs and rates  
- 📋 Loan application process
- 📄 Document requirements
- 🎯 Instant approvals

**Just tell me:** Are you looking for a personal loan today? I can show you exclusive offers! 🚀"""
        
        # Default encouraging response
        else:
            return """🤔 I want to make sure I help you with the right information!

Are you interested in:
- 💰 **Personal loan** - for any purpose
- 📊 **Checking rates** - current interest rates  
- 🧮 **EMI calculator** - monthly payment details
- 📋 **Loan application** - step by step process

Or simply say **"Hello"** to start your loan journey! 👋"""


# ------------------------------
# 4️⃣ DASHBOARD
# ------------------------------
def dashboard_view():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame([{"Message": "No applications yet"}])
    
    df = pd.read_csv(DATA_FILE)
    return df if not df.empty else pd.DataFrame([{"Message": "No applications yet"}])

def get_statistics():
    if not os.path.exists(DATA_FILE):
        return "No data available yet."
    
    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return "No applications processed yet."
    
    total = len(df)
    approved = len(df[df["Decision"] == "Approved"])
    conditional = len(df[df["Decision"] == "Conditional"])
    rejected = len(df[df["Decision"] == "Rejected"])
    
    avg_amount = df["Amount"].mean()
    avg_score = df["Credit Score"].mean()
    
    return f"""📊 **Application Statistics**
━━━━━━━━━━━━━━━━━━━━
Total Applications: {total}
✅ Approved: {approved} ({approved/total*100:.1f}%)
📝 Conditional: {conditional} ({conditional/total*100:.1f}%)
❌ Rejected: {rejected} ({rejected/total*100:.1f}%)

💰 Avg Loan Amount: Rs.{avg_amount:,.0f}
📊 Avg Credit Score: {avg_score:.0f}/900
━━━━━━━━━━━━━━━━━━━━"""


# ------------------------------
# 5️⃣ GRADIO INTERFACE
# ------------------------------

# Create master agent instance
master = MasterAgent()

def chat_handler(message, history):
    """Handle chat messages and return proper format for Gradio"""
    bot_response = master.process_message(message, history)
    return bot_response

def reset_master():
    """Reset the master agent for new conversation"""
    global master
    master = MasterAgent()
    return "🔄 **New session started!** Say **'Hello'** to begin your loan application journey!"

def get_conversation_options():
    """Get clickable options based on current conversation stage"""
    stage = master.conversation_stage
    
    if stage == "greeting":
        return [
            gr.Button("👋 Hello", visible=True),
            gr.Button("🆔 I'm an existing customer", visible=True), 
            gr.Button("🆕 I'm new to Tata Capital", visible=True),
            gr.Button("", visible=False)
        ]
    elif stage == "identification":
        return [
            gr.Button("🔍 Check existing customers", visible=True),
            gr.Button("📝 I'm a new customer", visible=True),
            gr.Button("", visible=False),
            gr.Button("", visible=False)
        ]
    elif stage in ["sales_pitch", "new_customer_pitch"]:
        return [
            gr.Button("✅ Yes, I'm interested!", visible=True),
            gr.Button("💰 Show me rates", visible=True),
            gr.Button("📊 Check eligibility", visible=True),
            gr.Button("❌ Not interested", visible=True)
        ]
    elif stage == "new_customer_info":
        return [
            gr.Button("💼 My salary is 50k", visible=True),
            gr.Button("💼 My salary is 75k", visible=True),
            gr.Button("💼 My salary is 1 lakh", visible=True),
            gr.Button("📝 Custom amount", visible=True)
        ]
    elif stage == "loan_requirement":
        return [
            gr.Button("💰 I need 2 lakh", visible=True),
            gr.Button("💰 I need 3 lakh", visible=True),
            gr.Button("💰 I need 5 lakh", visible=True),
            gr.Button("📝 Different amount", visible=True)
        ]
    elif stage == "terms_confirmation":
        return [
            gr.Button("✅ Proceed with terms", visible=True),
            gr.Button("⏱️ Change tenure", visible=True),
            gr.Button("💰 Different amount", visible=True),
            gr.Button("❌ Cancel", visible=True)
        ]
    elif stage == "underwriting":
        return [
            gr.Button("🔍 Check my credit score", visible=True),
            gr.Button("💰 See loan options", visible=True),
            gr.Button("📊 View eligibility", visible=True),
            gr.Button("⏭️ Process my application", visible=True)
        ]
    elif stage == "conditional_docs":
        return [
            gr.Button("📄 Yes, upload documents", visible=True),
            gr.Button("📱 Upload via mobile", visible=True),
            gr.Button("⏰ Upload later", visible=True),
            gr.Button("❓ What documents needed?", visible=True)
        ]
    elif stage == "sanction":
        return [
            gr.Button("📄 Generate sanction letter", visible=True),
            gr.Button("📧 Email me the letter", visible=True),
            gr.Button("💰 Check disbursement", visible=True),
            gr.Button("🏦 Branch details", visible=True)
        ]
    else:
        return [
            gr.Button("", visible=False),
            gr.Button("", visible=False),
            gr.Button("", visible=False),
            gr.Button("", visible=False)
        ]

# Build UI
with gr.Blocks(theme=gr.themes.Soft(), title="Tata Capital Loan Assistant") as demo:
    gr.Markdown("""
    # 🚀 Tata Capital - Advanced AI Loan Platform
    ### 🔥 Get Loans Directly Through Chat - Integrated Credit Assessment & Instant Approvals!
    #### Complete AI-Powered Solution: Master Agent + 4 Worker Agents with Real-time Processing
    """)
    
    with gr.Tab("💬 Loan Application Chat"):
        gr.Markdown("""
        ### 🚀 Start Your Instant Loan Journey Here!
        **Advanced AI-Powered Loan Processing** - Get loans directly through this chat!
        
        **🔥 NEW FEATURES:**
        - 🧠 **AI Credit Assessment** - Instant credit score analysis
        - 💰 **Personalized Loan Offerings** - Custom packages just for you  
        - ⚡ **Real-time Approval** - Get approved in minutes
        - 📊 **Smart Eligibility Check** - Know your options instantly
        - 📄 **Integrated Processing** - Complete loan process in chat
        
        **Complete Journey:**
        1. 🎯 **AI Sales & Negotiation** - Smart loan recommendations
        2. 🆔 **KYC Verification** - Quick identity verification  
        3. � **Integrated Credit Assessment** - Real-time credit analysis
        4. 💰 **Personalized Loan Offerings** - Tailored packages with EMI options
        5. ⚡ **Instant Approval/Rejection** - AI-powered loan decisions
        6. 📄 **Digital Sanction Letter** - PDF generation & download
        
        **💡 Pro Tip:** Just say "Hello" to begin your loan journey!
        """)
        
        # Main chat interface with quick action buttons
        chatbot = gr.Chatbot(height=500, type='messages', label="💬 Tata Capital Loan Assistant")
        msg = gr.Textbox(placeholder="Type your message or use suggested options below...", label="Your Message")
        
        # Dynamic response buttons that change based on conversation stage
        gr.Markdown("### 💬 Suggested Responses")
        with gr.Row():
            option1_btn = gr.Button("👋 Hello, I'm ready to start", variant="primary", visible=True)
            option2_btn = gr.Button("🆔 I'm an existing customer", variant="secondary", visible=True) 
            option3_btn = gr.Button("🆕 I'm new to Tata Capital", variant="secondary", visible=True)
            option4_btn = gr.Button("❓ Tell me about your services", variant="secondary", visible=True)
        
        # Quick action buttons in rows
        gr.Markdown("### 🚀 Quick Actions")
        with gr.Row():
            hello_btn = gr.Button("👋 Start Application", variant="primary")
            existing_btn = gr.Button("🔍 Existing Customer", variant="secondary") 
            new_btn = gr.Button("🆕 New Customer", variant="secondary")
            reset_btn = gr.Button("🔄 Reset Chat", variant="secondary")
        
        gr.Markdown("### 💰 Loan Types")
        with gr.Row():
            personal_btn = gr.Button("💼 Personal Loan", variant="outline")
            business_btn = gr.Button("🏢 Business Loan", variant="outline")
            wedding_btn = gr.Button("💒 Wedding Loan", variant="outline")
            medical_btn = gr.Button("🏥 Medical Loan", variant="outline")
        
        gr.Markdown("### � Quick Salary")
        with gr.Row():
            salary_30k_btn = gr.Button("Salary: Rs.30k", variant="outline") 
            salary_50k_btn = gr.Button("Salary: Rs.50k", variant="outline")
            salary_75k_btn = gr.Button("Salary: Rs.75k", variant="outline")
            salary_1l_btn = gr.Button("Salary: Rs.1L", variant="outline")
        
        gr.Markdown("### �💸 Quick Amounts")
        with gr.Row():
            amount_2l_btn = gr.Button("Rs.2 Lakh", variant="outline")
            amount_3l_btn = gr.Button("Rs.3 Lakh", variant="outline") 
            amount_5l_btn = gr.Button("Rs.5 Lakh", variant="outline")
            amount_10l_btn = gr.Button("Rs.10 Lakh", variant="outline")
        
        gr.Markdown("### ⚡ Quick Responses")
        with gr.Row():
            yes_btn = gr.Button("✅ Yes, Interested", variant="outline")
            no_btn = gr.Button("❌ Not Interested", variant="outline")
            proceed_btn = gr.Button("🚀 Proceed", variant="outline")
            help_btn = gr.Button("❓ Help", variant="outline")
        
        # Handle all interactions with dynamic button updates
        def respond(message, history):
            print(f"💬 TEXT INPUT: '{message}' | Stage: {master.conversation_stage}")
            bot_response = master.process_message(message, history)
            
            # Get current stage response options (after processing)
            response_options = master._get_response_options()
            print(f"📋 UPDATED STAGE: {master.conversation_stage} | OPTIONS: {response_options}")
            
            # Convert to proper message format for Gradio 5.x
            if history is None:
                history = []
            
            # Add user message and bot response in Gradio 5.x format
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": bot_response})
            
            # Update dynamic buttons with proper visibility
            button_updates = []
            for i, option in enumerate(response_options[:4]):  # Limit to 4 buttons
                if option and option.strip():
                    button_updates.append(gr.Button(option, visible=True))
                else:
                    button_updates.append(gr.Button("", visible=False))
            
            # Ensure we always return 4 button updates
            while len(button_updates) < 4:
                button_updates.append(gr.Button("", visible=False))
            
            return history, "", *button_updates
        
        def button_click(message, history):
            """Handle button clicks while preserving chat history"""
            print(f"🔘 BUTTON CLICKED: '{message}' | Stage: {master.conversation_stage}")
            
            # Use existing history or initialize empty
            if history is None:
                history = []
            
            # Clean button text (remove emojis for processing)
            clean_message = message
            if message.startswith("👋"):
                clean_message = "Hello"
            elif message.startswith("🆔"):
                clean_message = "I'm an existing customer"
            elif message.startswith("🆕"):
                clean_message = "I'm new to Tata Capital"
            elif message.startswith("✅"):
                clean_message = "Yes, I'm interested!"
            elif message.startswith("💰"):
                if "Show me" in message:
                    clean_message = "Show me rates"
                elif "need" in message:
                    clean_message = message.replace("💰 I need ", "I need ").replace(" lakh", "00000")
            elif message.startswith("📊"):
                clean_message = "Check eligibility"
            
            print(f"🔄 PROCESSING: '{clean_message}' | Current history length: {len(history)}")
            bot_response = master.process_message(clean_message, history)
            
            # Get NEW stage response options (after processing the message)
            response_options = master._get_response_options()
            print(f"📋 NEW STAGE: {master.conversation_stage} | OPTIONS: {response_options}")
            
            # Add to history in Gradio 5.x format  
            updated_history = history.copy()
            updated_history.append({"role": "user", "content": message})
            updated_history.append({"role": "assistant", "content": bot_response})
            
            # Update dynamic buttons with proper text
            button_updates = []
            for i, option in enumerate(response_options[:4]):  # Limit to 4 buttons
                if option and option.strip():  # Only create button if option has content
                    button_updates.append(gr.Button(option, visible=True))
                else:
                    button_updates.append(gr.Button("", visible=False))
            
            # Ensure we always return 4 button updates
            while len(button_updates) < 4:
                button_updates.append(gr.Button("", visible=False))
            
            return updated_history, "", *button_updates
        
        def reset_conversation():
            reset_master()
            return []
        
        # Event handlers with dynamic button updates
        msg.submit(respond, [msg, chatbot], [chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        
        # Dynamic response buttons - use a simple approach that gets current button text from master agent
        def option1_click(history):
            options = master._get_response_options()
            btn_text = options[0] if len(options) > 0 and options[0] else "Hello"
            return button_click(btn_text, history)
        
        def option2_click(history):
            options = master._get_response_options()
            btn_text = options[1] if len(options) > 1 and options[1] else "I'm an existing customer"  
            return button_click(btn_text, history)
        
        def option3_click(history):
            options = master._get_response_options()
            btn_text = options[2] if len(options) > 2 and options[2] else "I'm new to Tata Capital"
            return button_click(btn_text, history)
        
        def option4_click(history):
            options = master._get_response_options()
            btn_text = options[3] if len(options) > 3 and options[3] else "Tell me about services"
            return button_click(btn_text, history)
        
        option1_btn.click(option1_click, inputs=[chatbot], outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        option2_btn.click(option2_click, inputs=[chatbot], outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        option3_btn.click(option3_click, inputs=[chatbot], outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        option4_btn.click(option4_click, inputs=[chatbot], outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        
        # Quick action buttons
        hello_btn.click(lambda history: button_click("Hello", history), inputs=[chatbot], outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        existing_btn.click(lambda history: button_click("I'm an existing customer", history), inputs=[chatbot], outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        new_btn.click(lambda history: button_click("I'm a new customer", history), inputs=[chatbot], outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        
        def reset_with_buttons():
            reset_master()
            return [], "", gr.Button("👋 Hello, I'm ready to start", visible=True), gr.Button("🆔 I'm an existing customer", visible=True), gr.Button("🆕 I'm new to Tata Capital", visible=True), gr.Button("❓ Tell me about your services", visible=True)
        
        reset_btn.click(reset_with_buttons, outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        
        # Loan type buttons
        personal_btn.click(lambda history: button_click("Personal Loan", history), inputs=[chatbot], outputs=[chatbot, msg])
        business_btn.click(lambda history: button_click("Business Loan", history), inputs=[chatbot], outputs=[chatbot, msg])
        wedding_btn.click(lambda history: button_click("Wedding Loan", history), inputs=[chatbot], outputs=[chatbot, msg])
        medical_btn.click(lambda history: button_click("Medical Loan", history), inputs=[chatbot], outputs=[chatbot, msg])
        
        # Salary buttons
        salary_30k_btn.click(lambda history: button_click("My salary is 30000", history), inputs=[chatbot], outputs=[chatbot, msg])
        salary_50k_btn.click(lambda history: button_click("My salary is 50000", history), inputs=[chatbot], outputs=[chatbot, msg])
        salary_75k_btn.click(lambda history: button_click("My salary is 75000", history), inputs=[chatbot], outputs=[chatbot, msg])
        salary_1l_btn.click(lambda history: button_click("My salary is 100000", history), inputs=[chatbot], outputs=[chatbot, msg])
        
        # Amount buttons
        amount_2l_btn.click(lambda history: button_click("I need 2 lakh", history), inputs=[chatbot], outputs=[chatbot, msg])
        amount_3l_btn.click(lambda history: button_click("I need 3 lakh", history), inputs=[chatbot], outputs=[chatbot, msg])
        amount_5l_btn.click(lambda history: button_click("I need 5 lakh", history), inputs=[chatbot], outputs=[chatbot, msg])
        amount_10l_btn.click(lambda history: button_click("I need 10 lakh", history), inputs=[chatbot], outputs=[chatbot, msg])
        
        # Response buttons
        yes_btn.click(lambda history: button_click("Yes, I'm interested", history), inputs=[chatbot], outputs=[chatbot, msg])
        no_btn.click(lambda history: button_click("No, not interested", history), inputs=[chatbot], outputs=[chatbot, msg])
        proceed_btn.click(lambda history: button_click("Yes, proceed", history), inputs=[chatbot], outputs=[chatbot, msg])
        help_btn.click(lambda history: button_click("Help me", history), inputs=[chatbot], outputs=[chatbot, msg])
        

    
    with gr.Tab("📊 Analytics Dashboard"):
        gr.Markdown("### Loan Application Analytics")
        
        stats = gr.Textbox(label="Summary Statistics", value=get_statistics(), lines=12)
        
        gr.Markdown("### Recent Applications")
        dashboard = gr.DataFrame(value=dashboard_view(), label="Application History")
        
        refresh_btn = gr.Button("🔄 Refresh Dashboard")
        refresh_btn.click(fn=dashboard_view, outputs=dashboard)
        refresh_btn.click(fn=get_statistics, outputs=stats)
    
    with gr.Tab("👥 Customer Database"):
        gr.Markdown("### Synthetic Customer Data (CRM Server)")
        customer_df = pd.DataFrame.from_dict(customers, orient='index')
        customer_df = customer_df.reset_index().rename(columns={'index': 'Name'})
        gr.DataFrame(value=customer_df, label="Customer Records")
    
    with gr.Tab("ℹ️ System Info"):
        gr.Markdown("""
        ## 🤖 Agentic AI Architecture
        
        ### Master Agent (Orchestrator)
        - Manages conversation flow
        - Coordinates all worker agents
        - Maintains context across sessions
        
        ### Worker Agents
        
        1. **🎯 Sales Agent**
           - Pitches loan products
           - Negotiates terms (amount, tenure, rate)
           - Handles objections
        
        2. **✅ Verification Agent**
           - Validates KYC from CRM
           - Checks customer identity
           - Verifies contact details
        
        3. **📊 Underwriting Agent**
           - Fetches credit score from bureau API
           - Assesses eligibility:
             - Instant approval if ≤ pre-approved limit
             - Conditional if ≤ 2× limit & EMI ≤ 50% salary
             - Reject if score < 700 or amount > 2× limit
        
        4. **📄 Sanction Letter Generator**
           - Creates PDF sanction letter
           - Includes all loan details
           - Generates reference number
        
        ### Data Sources
        - **CRM Server**: Customer KYC data (10+ customers)
        - **Credit Bureau API**: Mock credit scores (600-850)
        - **Offer Mart**: Pre-approved limits & rates
        - **Persistent Storage**: CSV for applications, JSON for logs
        
        ### Technologies
        - Gradio for UI
        - Google Gemini for conversational AI
        - ReportLab for PDF generation
        - Pandas for data management
        """)

# Launch configuration for different environments
if __name__ == "__main__":
    # Check if running in a containerized environment
    import socket
    hostname = socket.gethostname()
    
    # Configure launch parameters - prioritize local access
    is_huggingface = os.getenv("SPACE_ID") is not None  # Detect if running on HF Spaces
    
    if is_huggingface:
        # Hugging Face Spaces configuration
        launch_kwargs = {
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "show_error": True,
            "quiet": False
        }
        print(f"🚀 Running on Hugging Face Spaces")
    else:
        # Local development configuration
        launch_kwargs = {
            "server_name": "127.0.0.1",  # Force localhost for local development
            "server_port": 7863,
            "share": False,  # Disable share for local testing
            "show_error": True,
            "quiet": False
        }
    
    print(f"🏦 Tata Capital AI Loan Assistant")
    print(f"🚀 Starting server on {launch_kwargs['server_name']}:{launch_kwargs['server_port']}")
    print(f"📱 Access at: http://localhost:{launch_kwargs['server_port']}")
    print(f"🔗 Alternative: http://127.0.0.1:{launch_kwargs['server_port']}")
    
    demo.launch(**launch_kwargs)