"""
PhishGuard AI — Seed Training Data

Curated dataset of labeled emails for training the ML classifier.
Labels: 0=safe, 1=suspicious, 2=phishing
"""


def get_seed_data() -> tuple[list[str], list[int]]:
    """Returns (texts, labels) for training. ~130 samples across 3 classes."""

    data = [
        # ══════════════════════════════════════════════════════
        # PHISHING EXAMPLES (label=2)
        # ══════════════════════════════════════════════════════
        ("Urgent: Your PayPal account has been limited. We noticed unusual activity and have temporarily restricted your account. Click here to verify your identity immediately to restore full access: http://paypa1-secure.tk/verify", 2),
        ("FINAL WARNING: Your Apple ID will be permanently disabled within 24 hours unless you verify your account information. Click the link below to confirm your identity: http://apple-id-verify.ga/login", 2),
        ("Dear Customer, We detected unauthorized access to your bank account. For your security, please confirm your identity by entering your credentials at: http://192.168.1.1/secure-banking", 2),
        ("Congratulations! You have been selected as the winner of our $1,000,000 lottery! To claim your prize, provide your full name, date of birth, and bank account details.", 2),
        ("Subject: Invoice #INV-2024-0847 OVERDUE. Your invoice is past due. Immediate payment required to avoid legal action. Click to view invoice: http://invoice-payment.xyz/view", 2),
        ("Your Netflix subscription payment failed. Update your payment method immediately or your account will be suspended: http://netfl1x-billing.tk/update", 2),
        ("IRS Notice: You are eligible for a tax refund of $4,287.00. Click here to claim your refund before it expires: http://irs-refund-claim.ml/submit", 2),
        ("From the desk of the CEO: I need you to purchase $500 in Amazon gift cards for a client meeting today. Please send me the codes ASAP. Keep this confidential.", 2),
        ("SECURITY ALERT: Someone tried to sign in to your Google account from Nigeria. If this wasn't you, secure your account immediately: http://g00gle-security.cf/alert", 2),
        ("Dear sir/madam, I am Prince Adebayo from Nigeria. I have $15.5 million USD inheritance that needs a trusted partner. Please send your bank details for the transfer.", 2),
        ("Your Microsoft 365 password expires today! Click here to keep your current password: http://microsoft-365-login.xyz/password-reset", 2),
        ("ACTION REQUIRED: Your Amazon order #112-4567890 has been held. Verify your payment information to release the package: http://amaz0n-delivery.ga/verify", 2),
        ("FEDEX: Your package delivery failed. Reschedule delivery by confirming your address and paying a $3.99 redelivery fee: http://fedex-redelivery.tk/pay", 2),
        ("WARNING: Your computer has been infected with malware. Call Microsoft Technical Support immediately at 1-800-555-0199 to fix this issue.", 2),
        ("Congrats! You've won a free iPhone 15 Pro! Click here to claim before offer expires in 2 hours: http://free-iphone-giveaway.win/claim", 2),
        ("Your Chase bank account shows suspicious transactions. Verify your identity now to prevent account closure: http://chase-secure-login.ml/verify", 2),
        ("HR Department: Due to a system upgrade, all employees must re-enter their login credentials at: http://company-portal.tk/login", 2),
        ("Bitcoin Investment Opportunity! Invest $500 today and earn $50,000 in just 30 days! Limited spots available. Send BTC to wallet: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", 2),
        ("Your Wells Fargo account has been locked due to security concerns. Verify your SSN and account number to unlock: http://wellsfarg0-secure.ga/unlock", 2),
        ("URGENT: Wire transfer of $25,000 needed today for the acquisition deal. The account details are attached. Please process immediately and keep this between us.", 2),
        ("You have (1) new voicemail from your bank. Listen now: http://voicemail-notification.xyz/listen. Enter your phone banking PIN to access.", 2),
        ("LinkedIn: Someone viewed your profile 47 times! See who's looking: http://linkedln-views.tk/profile", 2),
        ("Your WhatsApp account is about to expire! Verify now to continue using WhatsApp: http://whatsapp-verify.ga/renew", 2),
        ("NOTICE: Court summons regarding case #2024-CR-0284. Review the attached document immediately or face contempt of court charges.", 2),
        ("Dear valued customer, your account password was reset. If you did not request this, click here to secure your account: http://account-security.ml/reset", 2),
        ("Job Offer: Work from home and earn $5,000/week! No experience required. Send your resume and bank details to start immediately.", 2),
        ("Your DHL shipment is being held at customs. Pay the $4.50 customs fee to release your package: http://dhl-customs.xyz/pay", 2),
        ("IMPORTANT: Your Social Security Number has been compromised. Call immediately to prevent identity theft: 1-888-555-0123", 2),
        ("Refund Notice: You are owed a refund of $349.99 from your recent purchase. Click to process your refund: http://refund-process.tk/claim", 2),
        ("Dropbox: Someone shared a document with you. View the shared file: http://dropbox-shared.ga/view?file=confidential", 2),

        # ══════════════════════════════════════════════════════
        # SUSPICIOUS EXAMPLES (label=1)
        # ══════════════════════════════════════════════════════
        ("Hi, I noticed you haven't updated your account preferences in a while. Please take a moment to review your settings. Click here: http://account-preferences.com/update", 1),
        ("Dear user, as part of our annual security review, we kindly ask you to verify your email address by clicking the link below.", 1),
        ("Your subscription is about to expire. Renew now to continue enjoying our services without interruption.", 1),
        ("We noticed your profile is incomplete. Complete your profile to get better matches and recommendations.", 1),
        ("Important update regarding your account. Please log in to review recent changes to our terms of service.", 1),
        ("Reminder: Your free trial ends in 3 days. Enter payment details to continue using premium features.", 1),
        ("You have an unclaimed reward point balance of 5,000 points. Redeem before they expire at the end of this month.", 1),
        ("Your annual membership renewal is coming up. Review your plan and payment method to ensure uninterrupted access.", 1),
        ("System notification: Please update your recovery email and phone number for account security purposes.", 1),
        ("Dear member, we're upgrading our security protocols. You may be asked to re-authenticate on your next login.", 1),
        ("Survey invitation: Share your feedback and get a chance to win a $100 gift card. Limited time only.", 1),
        ("Your cloud storage is 90% full. Upgrade your plan or delete unused files to prevent data loss.", 1),
        ("Reminder: Your invoice #10234 is due in 5 business days. Please arrange payment to avoid late fees.", 1),
        ("New login detected from an unrecognized device. If this was you, no action needed. If not, review your security settings.", 1),
        ("We noticed some changes to our privacy policy that may affect your account. Please review the updated terms.", 1),
        ("Your order has been shipped but requires address confirmation. Please verify your delivery address.", 1),
        ("Account notification: Your saved payment method will expire next month. Update to avoid service interruption.", 1),
        ("Hello, this is a reminder about your upcoming appointment. Please confirm or reschedule at your convenience.", 1),
        ("Your account was accessed from a new location. Review recent activity to ensure your account is secure.", 1),
        ("Special offer: Get 50% off your next purchase! This exclusive deal is only available for the next 48 hours.", 1),

        # ══════════════════════════════════════════════════════
        # SAFE EXAMPLES (label=0)
        # ══════════════════════════════════════════════════════
        ("Hi team, please find the meeting notes from today's sprint planning session attached. Let me know if I missed anything.", 0),
        ("Hey! Just wanted to check if you're still available for coffee this Saturday at 3pm. Looking forward to catching up!", 0),
        ("Dear applicant, thank you for applying to the Software Engineer position. We would like to schedule an interview for next week.", 0),
        ("Your monthly bank statement for June 2024 is now available in your online banking portal. Log in to view.", 0),
        ("Hi Sarah, I've reviewed the project proposal and I think we should proceed with Option B. Let's discuss tomorrow.", 0),
        ("Team update: We've successfully deployed version 2.5 to production. All tests passed and monitoring looks good.", 0),
        ("Reminder: Company all-hands meeting is scheduled for Friday at 2pm EST. Agenda has been shared in Slack.", 0),
        ("Hi, your Amazon order #112-8901234 has been delivered to your front door. We hope you enjoy your purchase!", 0),
        ("Dear parent, this is a reminder that parent-teacher conferences are scheduled for next Thursday evening.", 0),
        ("Hey Mark, I finished the code review for PR #247. Left a few comments — mostly looks great. Nice work on the refactor!", 0),
        ("Newsletter: This week in tech — Apple announces new MacBook lineup, Google releases Gemini 2.0, and more.", 0),
        ("Your flight confirmation for LAX to JFK on July 15, departing at 8:30 AM. Booking reference: ABC123.", 0),
        ("Hi everyone, the quarterly revenue report is ready for review. I've uploaded it to the shared drive. Key highlights in the summary.", 0),
        ("Thank you for your donation of $50 to the Children's Education Fund. Your generosity makes a difference.", 0),
        ("Good morning! Here's your daily weather forecast: Sunny with a high of 78°F. Have a great day!", 0),
        ("Congratulations on your work anniversary! Thank you for 5 wonderful years with our company.", 0),
        ("Hi Dr. Johnson, I'm writing to schedule my annual checkup. Are there any openings next week?", 0),
        ("The new employee onboarding documentation has been updated. Please review before the orientation session.", 0),
        ("Reminder: Your library books are due in 3 days. You can renew online or return them to any branch.", 0),
        ("Hi team, I've created the Jira tickets for the Q3 sprint. Please review and estimate by end of day.", 0),
        ("Your Spotify Wrapped 2024 is ready! See your top songs, artists, and listening stats for the year.", 0),
        ("Meeting recap: We agreed to launch the beta on March 15, with feature freeze on March 1. Action items below.", 0),
        ("Hi, thanks for reaching out about the apartment listing. It's still available. When would you like to schedule a tour?", 0),
        ("Order confirmation: Your order of 3 books from Barnes & Noble has been confirmed. Estimated delivery: 5-7 business days.", 0),
        ("Happy birthday! Wishing you a wonderful year ahead. Hope you have an amazing celebration today!", 0),
        ("Project update: The database migration completed successfully last night. All data integrity checks passed.", 0),
        ("Dear student, your grades for the Fall semester have been posted. Log into the student portal to view your transcript.", 0),
        ("Invitation: You're invited to Jane and Michael's wedding on September 20th. RSVP by August 1st.", 0),
        ("Your monthly electricity bill of $127.43 is due on July 15. Auto-pay is enabled for your account.", 0),
        ("Hi, I wanted to share this interesting article about machine learning trends in 2024. Thought you might enjoy it.", 0),
        ("Team lunch: Let's do Thai food this Friday. I've made a reservation at 12:30pm. See you there!", 0),
        ("Your gym membership has been renewed for another year. Your next billing date is January 1, 2025.", 0),
        ("Hi Alex, the design mockups for the mobile app are ready for review. I've shared them in Figma.", 0),
        ("Neighborhood update: Road construction on Main Street will begin next Monday and is expected to last 2 weeks.", 0),
        ("Your prescription refill is ready for pickup at Walgreens Pharmacy. Store hours: 9 AM - 9 PM.", 0),

        # Additional phishing samples (label=2)
        ("COVID-19 relief payment of $1,200 is pending. Submit your direct deposit information within 48 hours: http://stimulus-payment-update.tk/claim", 2),
        ("DocuSign: A document requires your signature. Review and sign immediately: http://docusign-secure-doc.ga/sign", 2),
        ("Your Coinbase wallet has been flagged. Verify ownership by entering your recovery phrase at: http://coinbase-wallet-verify.ml/restore", 2),
        ("IT Helpdesk: Mandatory password reset due to security breach. Reset here: http://it-portal-reset.tk/password", 2),
        ("Your Uber account payment method was declined. Update billing details to avoid suspension: http://uber-billing-update.ga/pay", 2),
        ("Bank of America Alert: Unusual wire transfer attempt blocked. Confirm it was you: http://bofa-security-alert.tk/confirm", 2),
        ("Your Steam account is locked for suspicious trading activity. Unlock by verifying payment info: http://steam-account-unlock.xyz/verify", 2),
        ("Payroll update required before Friday. Confirm your direct deposit routing number here: http://payroll-portal-update.tk/submit", 2),
        ("Your iCloud storage payment failed. Update card details within 12 hours: http://icloud-billing-verify.ga/update", 2),
        ("Legal notice: Copyright infringement detected on your IP address. Pay settlement fee to avoid prosecution: http://copyright-settlement.ml/pay", 2),
        ("Your eBay seller account will be suspended. Verify tax information immediately: http://ebay-seller-verify.tk/tax", 2),
        ("Zoom meeting recording shared with you contains sensitive content. View before deletion: http://zoom-recording-shared.ga/view", 2),
        ("Your TikTok account violated community guidelines. Appeal within 24 hours: http://tiktok-appeal-center.tk/submit", 2),
        ("Western Union: Your transfer is on hold pending identity verification. Complete KYC: http://westernunion-kyc.ml/verify", 2),
        ("Your Shopify store payment gateway was disconnected. Reconnect to avoid order loss: http://shopify-gateway-reconnect.ga/setup", 2),

        # Additional suspicious samples (label=1)
        ("We detected a login attempt from a new browser. Review recent sign-in activity in your account security center.", 1),
        ("Your package delivery window has changed. Confirm your availability for redelivery this week.", 1),
        ("Action suggested: Review permissions for third-party apps connected to your account.", 1),
        ("Your membership benefits are expiring soon. Compare renewal options on your account page.", 1),
        ("We updated our refund policy. Please review changes that may affect recent purchases.", 1),
        ("Your document shared via cloud storage will expire in 7 days unless you extend access.", 1),
        ("Reminder: Complete your profile verification to unlock additional account features.", 1),
        ("Your recent transaction requires additional review. Sign in to provide confirmation details.", 1),
        ("Promotional credit of $10 will expire if unused by month end. View eligible purchases.", 1),
        ("Security tip: Enable two-factor authentication to protect your account from unauthorized access.", 1),
        ("Your service plan includes a pending upgrade. Accept or decline before the next billing cycle.", 1),
        ("We noticed inactive sessions on your account. Review and sign out unused devices.", 1),
        ("Your warranty registration is incomplete. Add product details to activate coverage.", 1),
        ("Invoice reminder: Payment is due in 3 days. View statement in your customer portal.", 1),
        ("Your loyalty points will expire unless redeemed this quarter. Browse available rewards.", 1),

        # Additional safe samples (label=0)
        ("Attached is the Q2 budget spreadsheet with updated forecasts. Please review before Monday's finance meeting.", 0),
        ("Thanks for submitting your expense report. Finance approved reimbursement — expect deposit within 5 business days.", 0),
        ("The CI pipeline passed on branch feature/auth-refactor. Ready for your review when you have time.", 0),
        ("Reminder: Dental cleaning appointment on Thursday at 10:30 AM. Reply to confirm or reschedule.", 0),
        ("Your GitHub pull request #892 received approval from two reviewers. You can merge when ready.", 0),
        ("Parking permit renewal for Zone B is open until March 31. Renew online through the city portal.", 0),
        ("Team offsite agenda draft is in Confluence. Add discussion topics by EOD Wednesday.", 0),
        ("Your car service appointment at AutoCare is confirmed for Saturday 9:00 AM.", 0),
        ("The HOA board meeting minutes from last month are attached for your records.", 0),
        ("Welcome to the hiking group! Our next trail is Eagle Ridge — meet at the north parking lot at 7 AM.", 0),
        ("Your tax documents from Acme Corp are available for download in the employee portal.", 0),
        ("Recipe swap this weekend — I'll bring the chili. Let me know if you want to host or come here.", 0),
        ("The webinar recording from yesterday's ML security talk is now on the internal wiki.", 0),
        ("Your child's school photo order deadline is Friday. Order forms were sent home in backpacks.", 0),
        ("Server maintenance completed successfully. No action required — all services are operational.", 0),
    ]

    texts = [d[0] for d in data]
    labels = [d[1] for d in data]

    return texts, labels
