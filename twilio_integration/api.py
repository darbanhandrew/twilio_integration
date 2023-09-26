from twilio.rest import Client
from frappe import _
import frappe
from twilio.base.exceptions import TwilioRestException

def update_phone_verified_status(user, status):
    try:
        # Get the last document for the current user
        doc = frappe.get_last_doc("Customer Profile", filters={"user": user})

        if doc:
            # Update the "phone_verified" field to the specified status
            doc.phone_verified = status
            doc.save()
    except Exception as e:
        frappe.log_error(_("Error updating phone_verified status: {0}").format(str(e)))

@frappe.whitelist()
def send_verification_code():
    try:
        # Get the phone number from the request
        to = frappe.form_dict.get("to")

        twilio_settings = frappe.get_doc("Twilio Settings","Twilio Settings",ignore_permissions=True)

        #Initialize the Twilio client with settings from the document
        client = Client(twilio_settings.account_sid, twilio_settings.auth_token)

        # Create a verification service
        verify = client.verify.v2.services(twilio_settings.service_id)

        # Send verification
        verification = verify.verifications.create(to=to, channel='sms')

        # Update the "phone_verified" field to False for the current user
        update_phone_verified_status(frappe.session.user, False)

        frappe.response["message"]={"status":"true"}
    except Exception as e:
        frappe.response["messsage"]=e

@frappe.whitelist()
def verify_verification_code():
    try:
        # Get the phone number and code from the request
        to = frappe.form_dict.get("to")
        code = frappe.form_dict.get("code")

        # Fetch Twilio settings from the "Twilio Settings" DocType
        twilio_settings = frappe.get_doc("Twilio Settings","Twilio Settings",ignore_permissions=True)

        # Initialize the Twilio client with settings from the document
        client = Client(twilio_settings.account_sid, twilio_settings.auth_token)

        # Create a verification service
        verify = client.verify.v2.services(twilio_settings.service_id)

        # Check verification
        result = verify.verification_checks.create(to=to, code=code)
        frappe.response["message"] = {"status":result.status}
        #   update_phone_verified_status(frappe.session.user, True)
    except Exception as e:
        frappe.response["message"] = e
