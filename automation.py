from whatsapp import send_whatsapp
def handle_hot_lead(lead):

    print("🔥 HOT LEAD DETECTED")
    
    send_whatsapp(lead.phone, lead.name)

    print(f"""
    New Hot Lead

    Name: {lead.name}
    Email: {lead.email}
    Phone: {lead.phone}
    Budget: {lead.budget}

    Agent should contact immediately.
    """)

    # aquí después podemos conectar WhatsApp o email