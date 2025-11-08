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
if api_key:
    genai.configure(api_key=api_key)
    print("✅ Gemini AI configured successfully")
else:
    print("ℹ️ Running without Gemini AI - using built-in responses")

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

🚀 **You have a SPECIAL pre-approved loan of ₹{limit:,}** waiting for you!

✨ **Your VIP Benefits:**
• 🏆 **Premium rate**: Just **10.99% p.a.** (Market rate: 12-18%)
• ⚡ **30-second approval** - No waiting, no hassles!
• 💳 **Flexible EMIs**: Choose 12-60 months
• 🎯 **Zero processing fees** (Save ₹{int(limit*0.02):,}!)
• 📱 **100% digital** - Apply from home

"""
        
        if credit_score >= 750:
            pitch += f"⭐ **GOLD CUSTOMER** - Your excellent credit score ({credit_score}) gets you the **BEST RATES**!\n\n"
        elif credit_score >= 700:
            pitch += f"✅ **QUALIFIED CUSTOMER** - Your good credit score ({credit_score}) ensures **INSTANT APPROVAL**!\n\n"
            
        if current_loans:
            pitch += f"🤝 **LOYAL CUSTOMER BONUS** - Existing relationship = **Additional 0.25% discount**!\n\n"
        
        pitch += f"""� **URGENCY ALERT**: This pre-approved offer expires in 7 days!

🎯 **Ready to claim your ₹{limit:,}?** 
Just tell me how much you need right now - from ₹50,000 to ₹{limit:,}!

Type your amount like: **"I need 2 lakh"** or **"₹300000"** 👇"""
        
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
💰 Loan Amount: ₹{amount:,}
⏱️ Tenure: {tenure} months  
📊 Interest Rate: {rate}% p.a.
💳 Monthly EMI: ₹{emi:,.2f}
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
• 📱 Upload via app (5 minutes)
• 🏦 Visit nearest branch  
• 📞 Video KYC call

⚠️ **Note:** Cannot proceed with loan without KYC completion."""
        
        # Handle new customers
        elif customer_data:
            return f"""📋 **KYC Required for New Customer**
━━━━━━━━━━━━━━━━━━━━
👤 Name: {name}
🏙️ City: {customer_data['city']}
📊 Salary: ₹{customer_data['salary']:,}
━━━━━━━━━━━━━━━━━━━━

As a **new customer**, we need to verify your identity:

📄 **Required Documents:**
• Aadhaar Card (Identity proof)
• PAN Card (Tax ID)
• Latest salary slip
• Bank statement (last 3 months)

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
💰 Approved Amount: ₹{amount:,}
📊 Credit Score: {score}/900
✅ Within Pre-Approved Limit: ₹{limit:,}
💳 Monthly EMI: ₹{emi:,.2f}
🤖 AI Confidence: {confidence}%
━━━━━━━━━━━━━━━━━━━━
🎊 Congratulations! Your loan is approved instantly!"""
            result["status"] = "Approved"
        
        elif amount <= 2 * limit and emi_to_salary_ratio <= 50:
            result["decision"] = f"""📝 **CONDITIONAL APPROVAL**
━━━━━━━━━━━━━━━━━━━━
💰 Requested: ₹{amount:,}
📊 Pre-Approved Limit: ₹{limit:,}
💳 Monthly EMI: ₹{emi:,.2f}
💼 EMI/Salary Ratio: {emi_to_salary_ratio:.1f}%
━━━━━━━━━━━━━━━━━━━━
✅ Your application is conditionally approved!

📄 **Please upload:**
• Latest 3 months salary slips
• Last 6 months bank statement

Upload these and get instant approval!"""
            result["status"] = "Conditional"
        
        else:
            result["decision"] = f"""❌ **Application Declined**
━━━━━━━━━━━━━━━━━━━━
Requested: ₹{amount:,}
Pre-Approved Limit: ₹{limit:,}
Maximum Eligible: ₹{2*limit:,}
━━━━━━━━━━━━━━━━━━━━
The requested amount exceeds our lending criteria.
Consider applying for ₹{limit:,} for instant approval."""
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
            "• This sanction is valid for 30 days from the date of issue",
            "• Final disbursement subject to verification of documents",
            "• Pre-payment charges: 2% on outstanding principal",
            "• Please visit the nearest branch to complete formalities",
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
    
    def _get_ai_response(self, prompt, fallback_response):
        """Get AI response with fallback"""
        try:
            if api_key:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text
            else:
                return fallback_response
        except Exception as e:
            print(f"AI Error: {e}")
            return fallback_response
    
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
            return ["💼 My salary: ₹30k-50k", "💼 My salary: ₹50k-75k", "💼 My salary: ₹75k-1L", "💼 My salary: ₹1L+"]
        elif stage == "loan_requirement":
            return ["💰 I need ₹2 Lakh", "💰 I need ₹3-5 Lakh", "💰 I need ₹5-10 Lakh", "📝 Different amount"]
        elif stage == "loan_type_selection":
            return ["💼 Personal Loan", "🏢 Business Loan", "💒 Wedding Loan", "🏥 Medical Emergency"]
        elif stage == "terms_confirmation":
            return ["✅ Accept these terms", "⏱️ Different tenure", "💰 Different amount", "📋 Need more details"]
        elif stage == "final_approval":
            return ["📄 Generate sanction letter", "📧 Email me details", "📞 Call me back", "🏦 Visit branch"]
        else:
            return ["✅ Yes", "❌ No", "📞 Tell me more", "🔄 Start over"]
    
    def process_message(self, message, history):
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
• ✅ Complete KYC now (takes 5 minutes)
• 📱 Upload documents via mobile app
• 🏦 Visit nearest branch
• 📞 Schedule video KYC call

**Without KYC, I cannot proceed with your loan application.**
Would you like to complete it now? Just say "Yes"! 👇"""
            
            else:
                return """🔍 **KYC Verification Required**

As per **RBI guidelines**, all loan applications need verified KYC.

📄 **Quick Digital KYC:**
• Takes only **5 minutes**
• Upload documents from phone
• Instant verification
• No branch visit needed

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
💰 **₹50,000 crores** disbursed last year
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
• **Instant approval** for pre-approved amounts
• **No paperwork hassles** 
• **Competitive rates** starting 10.99%
• **Quick disbursement** in 24 hours

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
• "My salary is 50000" or "50k" or "₹50,000" 💰"""
                else:
                    self.conversation_stage = "loan_requirement"
                    return self._show_loan_type_benefits(loan_type)
            else:
                return """💼 **What type of loan do you need?**

🎯 **Choose your loan purpose:**

**Click one of the options or type:**
• **"Personal Loan"** - For any personal needs
• **"Business Loan"** - For business expansion  
• **"Home Renovation"** - For home improvements
• **"Wedding Loan"** - For wedding expenses
• **"Travel Loan"** - For vacation/travel
• **"Medical Loan"** - For medical emergencies
• **"Education Loan"** - For studies/courses

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
• Type amount like: **250000** or **2.5 lakh** or **₹300000**
• We offer loans from ₹50,000 to ₹50,00,000

💡 **Popular {loan_type} amounts:**
• ₹2,00,000 - Small needs
• ₹5,00,000 - Medium requirements  
• ₹10,00,000 - Large projects"""
        
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
• **"Yes"** - to proceed with verification
• **"Change tenure"** - to modify repayment period
• **"Different amount"** - to change loan amount

💡 Ready to get **instant approval**? Just say **"Yes"**! ✅"""
        
        # Stage 5.5: KYC Upload for New Customers
        elif self.conversation_stage == "kyc_upload":
            if any(word in msg for word in ["yes", "proceed", "upload", "digital", "sure"]):
                # Simulate successful KYC
                self.conversation_stage = "underwriting"
                return """✅ **Digital KYC Completed Successfully!**

📋 **Documents Verified:**
• ✅ Aadhaar Card - Verified
• ✅ PAN Card - Verified  
• ✅ Salary Slip - Verified
• ✅ Bank Statement - Verified

🎉 **Great! Your profile is now complete.**

⏳ **Running credit assessment...**"""
            else:
                self.conversation_stage = "completed"
                return """📋 **No problem!** You can complete KYC later.

**Your loan application will be saved as DRAFT.**

Visit any Tata Capital branch or complete digital KYC anytime at www.tatacapital.com

Thank you for your interest! 🙏"""
        
        # Stage 6: Underwriting
        elif self.conversation_stage == "underwriting":
            result = self.underwriting_agent.assess_eligibility(
                self.context["name"],
                self.context["amount"],
                self.context.get("tenure", 24),
                self.context.get("customer_data")
            )
            
            # Save to CSV - this will now work properly
            self._save_application(result)
            
            if result["status"] == "Approved":
                self.conversation_stage = "sanction"
                return result["decision"] + "\n\n" + self._offer_sanction_letter()
            elif result["status"] == "Conditional":
                self.conversation_stage = "conditional_docs"
                return result["decision"] + "\n\n📄 Would you like to upload documents now for instant approval?"
            else:
                self.conversation_stage = "completed"
                return result["decision"] + "\n\n" + self._end_conversation()
        
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
        
        # Fallback to context-aware responses
        return self._smart_response(message)
    
    def _greet_customer(self):
        self.conversation_stage = "identification"
        
        # AI-enhanced greeting
        ai_prompt = """
        Create a warm, professional greeting for a loan assistant AI.
        Include benefits of Tata Capital loans and ask for customer's name.
        Keep it under 150 words, use emojis, and be engaging.
        """
        
        ai_greeting = self._get_ai_response(ai_prompt, "")
        
        base_greeting = """👋 **Welcome to Tata Capital Digital Loan Assistant!** 👋

🏆 **India's Most Trusted NBFC** - Serving 30 lakh+ customers!

🚀 **Get Instant Personal Loans with:**
• ⚡ **30-second approval** process
• 💰 **Loans up to ₹50 lakhs** 
• 🏆 **Interest rates from 10.99%**
• 📱 **100% digital** - No branch visit needed!
• 🎯 **Same-day disbursement** available!

✨ **7 Loan Types Available:** Personal, Business, Wedding, Medical, Travel, Education, Home Renovation

**🔍 Let's start! May I know your name?** 
Type it below or choose from our customer database! 👇"""
        
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
                
                base_response = f"""🎉 **Welcome back, {existing_name}!** 🎉

🔍 **CUSTOMER PROFILE LOADED**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 **Name:** {existing_name}
📍 **City:** {customer_data['city']}
📞 **Phone:** {customer_data['phone']}
🆔 **KYC Status:** {kyc_status}
💳 **Credit Score:** {customer_data['credit_score']}/850 ({credit_rating})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **EXCLUSIVE VIP BENEFITS:**
• 🏆 **Pre-approved limit**: ₹{customer_data["pre_approved_limit"]:,}
• ⚡ **Instant approval** - Priority processing!
• 💰 **Special rate**: From **10.99% p.a.**
• 🎯 **Zero documentation** for pre-approved amounts!

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
            return f"""🎉 **Hello {name.title()}! Welcome to Tata Capital!**

🚀 **GREAT NEWS!** Even as a new customer, you can get:

✨ **INSTANT LOAN APPROVAL** up to ₹50 lakhs!
• 💰 **Best rates**: Starting from just **10.99% p.a.**
• ⚡ **Quick approval**: Decision in 30 seconds  
• 📱 **Digital process**: Apply from home
• 🏆 **No hidden charges**: Complete transparency

**💡 Ready to discover how much you can get approved for?**

Thousands of customers get **instant approval** daily! 
Want to check your eligibility right now? 🎯"""
    
    def _show_loan_pitch(self):
        self.conversation_stage = "loan_type_selection"
        return self.sales_agent.pitch_loan(
            self.context["name"],
            self.context["customer_data"]
        ) + "\n\n" + self._show_loan_types()
    
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
• ✅ **100% FREE** - No charges at all
• ⚡ **Takes 30 seconds** - Super quick
• 🔒 **Completely secure** - No spam calls
• 📱 **No paperwork** needed right now

**Think of it this way:** Wouldn't you want to know if you can get ₹10 lakhs at just 10.99% interest? 

Even if you don't need money today, **life is unpredictable**:
• Medical emergencies 🏥
• Home repairs 🏠  
• Wedding expenses 💒
• Business opportunities 💼

**Just say "Check" to see your FREE eligibility!** 
What have you got to lose? 🤔"""
    
    def _handle_objection(self):
        self.conversation_stage = "sales_pitch"  # Keep trying
        return """I completely understand! 😊 

But let me share something exciting - you already have **pre-approved offers** waiting! This means:

🎯 **ZERO paperwork** for pre-approved amounts
💰 **Instant approval** - no waiting days
📊 **Best rates** - starting from just 10.99%
✨ **No hidden charges** - complete transparency

Even if you don't need money right now, wouldn't you like to know your **FREE pre-approved limit**? It takes just 30 seconds! 

What do you say? Ready to discover your offer? 🚀"""
    
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

• **12 months** - Higher EMI, less interest
• **24 months** - Balanced option ⭐ 
• **36 months** - Lower EMI
• **48 months** - Very low EMI
• **60 months** - Lowest EMI

        Just tell me: "24 months" or "3 years" etc."""
    
    def _collect_new_customer_info(self, message):
        """Collect information from new customers step by step"""
        name = self.context["name"]
        
        # Step 1: Collect salary
        if "salary" not in self.context:
            salary = self._extract_salary(message)
            if salary:
                self.context["salary"] = salary
                return f"""💰 **Great! Monthly salary: ₹{salary:,}**

📋 **Step 2: Location** 
━━━━━━━━━━━━━━━━━━━━
Which city are you based in?

💡 **Examples:**
• "I'm in Mumbai"
• "Bangalore" 
• "Delhi NCR"

**Different cities have different offers!** 🏙️"""
            else:
                return """💰 **Please share your monthly salary:**

💡 **Examples:**
• "50000" or "50k"
• "My salary is 75000"
• "I earn ₹60,000 per month"

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
• "I'm 28 years old"
• "32"
• "Age 35"

**Younger professionals often get better rates!** ⭐"""
            else:
                return """🏙️ **Which city are you in?**

Just type your city name:
• Mumbai, Delhi, Bangalore, Pune, Chennai, Hyderabad, etc.

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
• "28" 
• "I'm 32 years old"
• "Age: 35"

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
💰 **Eligible Amount**: Up to **₹{limit:,}**
📊 **Estimated Credit Score**: {score}/900
⭐ **Interest Rate**: Starting from **10.99% p.a.**
💳 **Flexible Tenure**: 12 to 60 months
⚡ **Processing Time**: 30 seconds to 2 hours

"""
        
        if score >= 750:
            offer += "🏆 **PREMIUM CUSTOMER** - You qualify for our **LOWEST RATES**!\n\n"
        elif score >= 700:
            offer += "✅ **EXCELLENT PROFILE** - High approval chances!\n\n"
        
        offer += f"""💡 **Based on your ₹{salary:,} salary, you can easily afford:**
• ₹{int(limit/2):,} loan = ₹{self._calculate_emi(int(limit/2), 24):,}/month EMI
• ₹{int(limit*0.75):,} loan = ₹{self._calculate_emi(int(limit*0.75), 36):,}/month EMI

🎯 **Ready to apply? How much do you need today?**
Just tell me like: **"I need 3 lakh"** or **"₹500000"** 💰"""
        
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
• ✅ **No end-use restrictions** - Use for anything!
• ⚡ **Instant approval** for pre-approved customers
• 💰 **Up to ₹50 lakhs** available
• 🏆 **Lowest rates** starting 10.99%
• 📱 **100% digital process** - No branch visit

💡 **Perfect for:** Medical bills, debt consolidation, shopping, emergencies""",

            "Business Loan": """💼 **Business Loan - Grow Your Business!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
• 🚀 **Quick capital** for business growth
• 💰 **Up to ₹1 crore** funding available  
• 📊 **Flexible repayment** up to 5 years
• 💳 **Competitive rates** from 11.5%
• 📈 **No collateral** required up to ₹50L

💡 **Perfect for:** Inventory, expansion, equipment, working capital""",

            "Wedding Loan": """💒 **Wedding Loan - Make Your Day Special!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
• 🎉 **Wedding season discount** - Extra 0.5% off
• 💰 **Up to ₹25 lakhs** for your big day
• ⏱️ **Extended tenure** up to 5 years
• 🎁 **Free wedding planning** consultation
• 📱 **Quick approval** in 24 hours

💡 **Perfect for:** Venue, catering, jewelry, shopping, honeymoon""",

            "Home Renovation Loan": """🏠 **Home Renovation - Transform Your Space!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
• 🔨 **Renovation specialist** team support
• 💰 **Up to ₹30 lakhs** for home improvement
• 🏆 **Special rates** from 10.5% for home loans
• 📋 **Minimal documentation** required
• 🎯 **Vendor tie-ups** for discounts

💡 **Perfect for:** Kitchen, bathroom, flooring, painting, furnishing""",

            "Travel Loan": """✈️ **Travel Loan - Explore the World!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
• 🌍 **Travel partner discounts** up to 15%
• 💰 **Up to ₹15 lakhs** for dream vacations
• ⚡ **48-hour approval** for urgent travel
• 💳 **Zero forex markup** on international cards
• 📱 **Travel insurance** included

💡 **Perfect for:** International trips, family vacations, adventure tours""",

            "Medical Loan": """🏥 **Medical Loan - Health First Priority!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
• 🚨 **Emergency approval** in 2 hours
• 💰 **Up to ₹20 lakhs** for medical needs
• 🏆 **Lowest rates** from 9.99% (special rate)
• 🏥 **Hospital tie-ups** for direct payment
• 💊 **Medical insurance** guidance

💡 **Perfect for:** Surgery, treatment, medicines, health checkups""",

            "Education Loan": """🎓 **Education Loan - Invest in Your Future!**
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Special Benefits:**
• 📚 **Student-friendly** EMI options
• 💰 **Up to ₹1 crore** for higher studies
• 🎯 **Moratorium period** during studies
• 🌍 **International education** support
• 📜 **Tax benefits** under Section 80E

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
        return "🎉 Would you like me to generate your official sanction letter now?"
    
    def _generate_sanction(self):
        self.conversation_stage = "completed"
        name = self.context["name"]
        amount = self.context["amount"]
        tenure = self.context.get("tenure", 24)
        rate = 11.5
        
        filepath = self.sanction_generator.generate_pdf(
            name, amount, tenure, rate,
            self.context["customer_data"]
        )
        
        return f"""✅ **Sanction Letter Generated Successfully!**

📄 **Download your letter:** {filepath}

🎊 **Next Steps:**
1. Download and review your sanction letter
2. Visit nearest Tata Capital branch with:
   • Original ID proofs
   • Address proof
   • Bank statements (last 6 months)
3. Complete signing formalities
4. Get disbursement within 24 hours!

Thank you for choosing Tata Capital. Have a great day! 🙏"""
    
    def _end_conversation(self):
        return "\n\nThank you for considering Tata Capital. Feel free to reach out anytime! 🙏"
    
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
            
            print(f"✅ Application saved: {customer_name} - {result['status']} - ₹{amount:,}")
            
        except Exception as e:
            print(f"❌ Error saving application: {str(e)}")
            # Still continue the conversation even if saving fails
    
    def _smart_response(self, message):
        """Enhanced AI-powered smart responses with context awareness"""
        msg = message.lower()
        
        # Create AI prompt for intelligent conversation
        ai_prompt = f"""
        You are a professional loan assistant for Tata Capital NBFC. 
        Current conversation stage: {self.conversation_stage}
        Customer context: {self.context}
        Customer message: {message}
        
        Respond in a helpful, professional manner focusing on loan services.
        Keep response under 200 words and include relevant emojis.
        Always guide towards loan application completion.
        """
        
        # Try AI response first, then fallback to rule-based
        ai_response = self._get_ai_response(ai_prompt, None)
        if ai_response:
            return f"🤖 **AI Assistant:** {ai_response}\n\n💡 *Would you like to proceed with your loan application?*"
        
        # Enhanced rule-based responses
        if any(word in msg for word in ["loan", "money", "borrow", "credit", "finance"]):
            return """💰 **Perfect! You're in the right place!** 💰
            
🏆 **Tata Capital - India's #1 NBFC** offers:
• ✅ **Pre-approved limits** up to ₹50 lakhs
• ⚡ **30-second approval** process  
• 💳 **Flexible EMIs** from 12-60 months
• 🏆 **Interest rates from 10.99%**
• 📱 **100% digital** - No branch visits!

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
• ₹2 lakh loan = ₹9,500/month (24 months)
• ₹3 lakh loan = ₹14,200/month (24 months)  
• ₹5 lakh loan = ₹23,600/month (24 months)

🎯 **Flexible tenures:** 12 to 60 months
📱 **Auto-debit facility** available

Share your loan amount for exact EMI calculation!"""
        
        # Documents/requirements
        elif any(word in msg for word in ["document", "paper", "require", "need"]):
            return """📄 **Required Documents:**
            
**For Pre-approved customers:**
• Just your Aadhaar & PAN (already verified!)
• Bank statement (last 3 months)
• Salary slips (latest 2)

**For others:**
• Identity proof (Aadhaar/Passport/Driving License)
• Address proof  
• Income proof (salary slips/ITR)
• Bank statements (6 months)

💡 Pre-approved customers get **instant approval**! Check if you're pre-approved?"""
        
        # Help/support queries
        elif any(word in msg for word in ["help", "support", "contact"]):
            return """🤝 **I'm here to help!**
            
I can assist you with:
• ✅ Checking pre-approved loan offers
• 💰 Calculating EMIs and rates  
• 📋 Loan application process
• 📄 Document requirements
• 🎯 Instant approvals

**Just tell me:** Are you looking for a personal loan today? I can show you exclusive offers! 🚀"""
        
        # Default encouraging response
        else:
            return """🤔 I want to make sure I help you with the right information!

Are you interested in:
• 💰 **Personal loan** - for any purpose
• 📊 **Checking rates** - current interest rates  
• 🧮 **EMI calculator** - monthly payment details
• 📋 **Loan application** - step by step process

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

💰 Avg Loan Amount: ₹{avg_amount:,.0f}
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
    # 🏦 Tata Capital - AI Loan Assistant
    ### Complete Agentic AI Solution with Master Agent + Worker Agents
    """)
    
    with gr.Tab("💬 Loan Application Chat"):
        gr.Markdown("""
        ### Start Your Loan Journey Here!
        This AI assistant will guide you through:
        1. 🎯 Sales & Negotiation
        2. ✅ KYC Verification  
        3. 📊 Credit Assessment
        4. 📄 Sanction Letter Generation
        
        **Just say "Hello" to begin!**
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
            salary_30k_btn = gr.Button("Salary: ₹30k", variant="outline") 
            salary_50k_btn = gr.Button("Salary: ₹50k", variant="outline")
            salary_75k_btn = gr.Button("Salary: ₹75k", variant="outline")
            salary_1l_btn = gr.Button("Salary: ₹1L", variant="outline")
        
        gr.Markdown("### �💸 Quick Amounts")
        with gr.Row():
            amount_2l_btn = gr.Button("₹2 Lakh", variant="outline")
            amount_3l_btn = gr.Button("₹3 Lakh", variant="outline") 
            amount_5l_btn = gr.Button("₹5 Lakh", variant="outline")
            amount_10l_btn = gr.Button("₹10 Lakh", variant="outline")
        
        gr.Markdown("### ⚡ Quick Responses")
        with gr.Row():
            yes_btn = gr.Button("✅ Yes, Interested", variant="outline")
            no_btn = gr.Button("❌ Not Interested", variant="outline")
            proceed_btn = gr.Button("🚀 Proceed", variant="outline")
            help_btn = gr.Button("❓ Help", variant="outline")
        
        # Handle all interactions with dynamic button updates
        def respond(message, history):
            bot_response = master.process_message(message, history)
            
            # Get current stage response options
            response_options = master._get_response_options()
            
            # Convert to proper message format for Gradio 5.x
            if history is None:
                history = []
            
            # Add user message and bot response in Gradio 5.x format
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": bot_response})
            
            # Update dynamic buttons
            button_updates = []
            for i, option in enumerate(response_options[:4]):  # Limit to 4 buttons
                button_updates.append(gr.Button(option, visible=True))
            while len(button_updates) < 4:
                button_updates.append(gr.Button("", visible=False))
            
            return history, "", *button_updates
        
        def button_click(message):
            """Handle button clicks"""
            current_history = chatbot.value or []
            bot_response = master.process_message(message, current_history)
            
            # Get current stage response options
            response_options = master._get_response_options()
            
            # Add to history in Gradio 5.x format
            new_history = current_history.copy()
            new_history.append({"role": "user", "content": message})
            new_history.append({"role": "assistant", "content": bot_response})
            
            # Update dynamic buttons
            button_updates = []
            for i, option in enumerate(response_options[:4]):  # Limit to 4 buttons
                button_updates.append(gr.Button(option, visible=True))
            while len(button_updates) < 4:
                button_updates.append(gr.Button("", visible=False))
            
            return new_history, "", *button_updates
        
        def reset_conversation():
            reset_master()
            return []
        
        # Event handlers with dynamic button updates
        msg.submit(respond, [msg, chatbot], [chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        
        # Dynamic response buttons
        option1_btn.click(lambda btn: button_click(btn.value if hasattr(btn, 'value') else "Hello"), 
                         outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        option2_btn.click(lambda btn: button_click(btn.value if hasattr(btn, 'value') else "I'm an existing customer"), 
                         outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        option3_btn.click(lambda btn: button_click(btn.value if hasattr(btn, 'value') else "I'm new to Tata Capital"), 
                         outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        option4_btn.click(lambda btn: button_click(btn.value if hasattr(btn, 'value') else "Tell me about services"), 
                         outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        
        # Quick action buttons
        hello_btn.click(lambda: button_click("Hello"), outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        existing_btn.click(lambda: button_click("I'm an existing customer"), outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        new_btn.click(lambda: button_click("I'm a new customer"), outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        
        def reset_with_buttons():
            reset_master()
            return [], "", gr.Button("👋 Hello, I'm ready to start", visible=True), gr.Button("🆔 I'm an existing customer", visible=True), gr.Button("🆕 I'm new to Tata Capital", visible=True), gr.Button("❓ Tell me about your services", visible=True)
        
        reset_btn.click(reset_with_buttons, outputs=[chatbot, msg, option1_btn, option2_btn, option3_btn, option4_btn])
        
        # Loan type buttons
        personal_btn.click(lambda: button_click("Personal Loan"), outputs=[chatbot, msg])
        business_btn.click(lambda: button_click("Business Loan"), outputs=[chatbot, msg])
        wedding_btn.click(lambda: button_click("Wedding Loan"), outputs=[chatbot, msg])
        medical_btn.click(lambda: button_click("Medical Loan"), outputs=[chatbot, msg])
        
        # Salary buttons
        salary_30k_btn.click(lambda: button_click("My salary is 30000"), outputs=[chatbot, msg])
        salary_50k_btn.click(lambda: button_click("My salary is 50000"), outputs=[chatbot, msg])
        salary_75k_btn.click(lambda: button_click("My salary is 75000"), outputs=[chatbot, msg])
        salary_1l_btn.click(lambda: button_click("My salary is 100000"), outputs=[chatbot, msg])
        
        # Amount buttons
        amount_2l_btn.click(lambda: button_click("I need 2 lakh"), outputs=[chatbot, msg])
        amount_3l_btn.click(lambda: button_click("I need 3 lakh"), outputs=[chatbot, msg])
        amount_5l_btn.click(lambda: button_click("I need 5 lakh"), outputs=[chatbot, msg])
        amount_10l_btn.click(lambda: button_click("I need 10 lakh"), outputs=[chatbot, msg])
        
        # Response buttons
        yes_btn.click(lambda: button_click("Yes, I'm interested"), outputs=[chatbot, msg])
        no_btn.click(lambda: button_click("No, not interested"), outputs=[chatbot, msg])
        proceed_btn.click(lambda: button_click("Yes, proceed"), outputs=[chatbot, msg])
        help_btn.click(lambda: button_click("Help me"), outputs=[chatbot, msg])
        

    
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
    
    # Configure launch parameters
    launch_kwargs = {
        "server_name": "0.0.0.0" if os.getenv("GRADIO_SERVER_NAME") else "127.0.0.1",
        "server_port": int(os.getenv("GRADIO_SERVER_PORT", 7861)),
        "share": True,  # Set to True for temporary public sharing
        "show_error": True,
        "quiet": False
    }
    
    print(f"🏦 Tata Capital AI Loan Assistant")
    print(f"🚀 Starting server on {launch_kwargs['server_name']}:{launch_kwargs['server_port']}")
    print(f"📱 Access at: http://{'localhost' if launch_kwargs['server_name'] == '127.0.0.1' else launch_kwargs['server_name']}:{launch_kwargs['server_port']}")
    
    demo.launch(**launch_kwargs)