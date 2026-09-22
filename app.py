import streamlit as st
from supabase import create_client
from datetime import date

st.set_page_config(page_title="Issue Tracker", layout="wide")

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
sb = create_client(url, key)

def get_issues(category=None, status=None):
    q = sb.table("issues").select("*").order("due_date")
    if category:
        q = q.eq("category", category)
    if status:
        q = q.eq("status", status)
    return q.execute().data

def add_issue(title, category, due_date, report_back, recurring):
    sb.table("issues").insert({
        "title": title,
        "category": category,
        "due_date": str(due_date) if due_date else None,
        "report_back": report_back,
        "recurring": recurring,
    }).execute()

def get_notes(issue_id):
    return sb.table("notes").select("*").eq("issue_id", issue_id).order("created_at").execute().data

def add_note(issue_id, text):
    sb.table("notes").insert({"issue_id": issue_id, "note_text": text}).execute()

def update_status(issue_id, status):
    sb.table("issues").update({"status": status}).eq("id", issue_id).execute()

st.title("Issue Tracker")

with st.sidebar:
    st.header("New Issue")
    title = st.text_input("Title")
    category = st.radio("Category", ["finance", "sysadmin"])
    due = st.date_input("Due date", value=None)
    report_back = st.checkbox("Report-back item")
    recurring = st.checkbox("Recurring")
    if st.button("Add Issue") and title:
        add_issue(title, category, due, report_back, recurring)
        st.success("Added.")
        st.rerun()

tab1, tab2, tab3 = st.tabs(["Finance", "Sysadmin", "Report-Backs"])

def render_list(issues):
    for issue in issues:
        with st.expander(f"{issue['title']} — due {issue['due_date'] or 'none'} ({issue['status']})"):
            new_status = st.selectbox(
                "Status", ["open", "waiting", "closed"],
                index=["open", "waiting", "closed"].index(issue["status"]),
                key=f"status_{issue['id']}"
            )
            if new_status != issue["status"]:
                update_status(issue["id"], new_status)
                st.rerun()

            st.write("**Notes:**")
            for n in get_notes(issue["id"]):
                st.text(f"{n['created_at'][:10]}: {n['note_text']}")

            new_note = st.text_input("Add note", key=f"note_{issue['id']}")
            if st.button("Save note", key=f"save_{issue['id']}") and new_note:
                add_note(issue["id"], new_note)
                st.rerun()

with tab1:
    render_list(get_issues(category="finance"))

with tab2:
    render_list(get_issues(category="sysadmin"))

with tab3:
    all_issues = get_issues()
    render_list([i for i in all_issues if i["report_back"]])