import json
import os

DATA_FILE = "grades_data.json"

KNOWN_THRESHOLDS = {
    "Physics": [72.0, 36.0],
    "Chemistry": [66.0, 33.0],
    "Biology": [67.0, 35.0],
    "Mathematics": [80.0, 38.0],
    "Further Math": [73.0, 30.0],
    "Computer Science": [60.0, 30.0],
    "English General Paper": [66.0, 33.0],
    "English Language": [71.0, 35.0],
    "Economics": [65.0, 33.0],
    "Business": [65.0, 38.0],
    "Psychology": [66.0, 32.0],
    "Sociology": [66.0, 32.0],
}

def load_data():
    """Loads saved user data from a local JSON file if present."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[!] Saved data file corrupted. Starting fresh.")
    return {"subjects": [], "thresholds": KNOWN_THRESHOLDS.copy(), "pa_data": {}, "term_data": {}}

def save_data(data):
    """Saves current state to local JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def input_scores(prompt_text, min_val=0.0, max_val=100.0):
    """Handles numeric input validation with customizable min/max limits."""
    while True:
        try:
            score = float(input(prompt_text))
            if min_val <= score <= max_val:
                return score
            print(f"  [!] Enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("  [!] Invalid input. Enter a numerical value.")

def get_as_letter_grade(subject_name, percentage, thresholds_db):
    """Calculates letter grade (A-E) using threshold boundaries."""
    a_min, e_min = thresholds_db[subject_name]
    step = (a_min - e_min) / 4.0
    
    b_min = a_min - step
    c_min = b_min - step
    d_min = c_min - step

    if percentage >= a_min:
        return "A"
    elif percentage >= b_min:
        return "B"
    elif percentage >= c_min:
        return "C"
    elif percentage >= d_min:
        return "D"
    elif percentage >= e_min:
        return "E"
    else:
        return "U (Ungraded)"

def setup_subjects(data):
    """Configures subjects and prompts for missing thresholds."""
    print("=" * 55)
    print("           AS LEVEL SUBJECT CONFIGURATION")
    print("=" * 55)
    
    while True:
        try:
            num_subjects = int(input("How many subjects are you taking? (5 or 6): "))
            if num_subjects in [5, 6]:
                break
            print("  [!] Please enter either 5 or 6.")
        except ValueError:
            print("  [!] Enter a valid integer.")

    print("\nAvailable pre-configured subjects:")
    print(", ".join(data["thresholds"].keys()))
    print("\n(If you enter an unlisted subject, you will be asked to set its threshold)\n")

    user_subjects = []

    for i in range(1, num_subjects + 1):
        while True:
            sub = input(f"Enter name for Subject {i}: ").strip()
            if not sub:
                print("  [!] Name cannot be empty.")
                continue
            
            matched_key = next((k for k in data["thresholds"] if k.lower() == sub.lower()), sub.title())
            
            if matched_key in user_subjects:
                print("  [!] Subject already added. Enter a different subject.")
                continue

            user_subjects.append(matched_key)

            if matched_key not in data["thresholds"]:
                print(f"  [?] Threshold for '{matched_key}' is unknown.")
                a_min = input_scores(f"  -> Enter min percentage (%) needed for an 'A' in {matched_key}: ", 0.0, 100.0)
                
                while True:
                    e_min = input_scores(f"  -> Enter min percentage (%) needed for an 'E' in {matched_key}: ", 0.0, 100.0)
                    if e_min < a_min:
                        break
                    print("  [!] 'E' threshold must be lower than 'A' threshold.")

                data["thresholds"][matched_key] = [a_min, e_min]
                print(f"  [✓] Threshold set for {matched_key}: A >= {a_min}%, E >= {e_min}%\n")
            
            break

    data["subjects"] = user_subjects
    data["pa_data"] = {}
    data["term_data"] = {}
    save_data(data)
    print(f"\n[✓] Configured subjects: {', '.join(user_subjects)}\n")

def enter_personal_assessment(data):
    """Mode 1: Input or refresh best 4 unit test scores per subject."""
    print("\n" + "=" * 55)
    print("MODE 1: PERSONAL ASSESSMENT (40% Weightage)")
    print("=" * 55)

    for subject in data["subjects"]:
        print(f"\n--- {subject} ---")
        scores = []
        for i in range(1, 5):
            print(f"  Test {i}:")
            obtained = input_scores("    Marks obtained: ", min_val=0.0, max_val=1000.0)
            total = input_scores("    Total possible marks: ", min_val=0.1, max_val=1000.0)
            
            scores.append((obtained / total) * 100)
        
        avg_percentage = sum(scores) / len(scores)
        data["pa_data"][subject] = {
            "average": avg_percentage,
            "raw_scores": scores
        }
        print(f"  -> {subject} PA Average: {avg_percentage:.2f}%")
    
    save_data(data)
    print("\n[✓] Personal Assessment scores saved to disk!\n")

def enter_terminal_exam(data):
    """Mode 2: Input terminal examination percentages."""
    print("\n" + "=" * 55)
    print("MODE 2: TERMINAL EXAMINATION (60% Weightage)")
    print("=" * 55 + "\n")

    for subject in data["subjects"]:
        score = input_scores(f"Enter Terminal Exam percentage for {subject} (0-100%): ", min_val=0.0, max_val=100.0)
        data["term_data"][subject] = score
    
    save_data(data)
    print("\n[✓] Terminal Examination scores saved to disk!\n")

def update_marks(data):
    """Allows updating specific scores for an existing subject."""
    if not data["subjects"]:
        print("\n[!] No subjects configured yet.")
        return

    print("\n" + "=" * 55)
    print("                UPDATE MARKS SYSTEM")
    print("=" * 55)
    print("Select a subject to update:")
    for i, sub in enumerate(data["subjects"], 1):
        print(f"{i}. {sub}")
    
    choice = input_scores("\nSelect subject number: ", min_val=1, max_val=len(data["subjects"]))
    selected_subject = data["subjects"][int(choice) - 1]

    print(f"\nUpdating marks for {selected_subject}:")
    print("1. Update Personal Assessment Test Score")
    print("2. Update Terminal Exam Score")
    print("3. Cancel")
    
    up_choice = input("\nSelect option (1-3): ").strip()

    if up_choice == "1":
        if selected_subject not in data["pa_data"]:
            data["pa_data"][selected_subject] = {"raw_scores": [0.0] * 4, "average": 0.0}

        print(f"\nCurrent PA raw percentages for {selected_subject}:")
        for i, score in enumerate(data["pa_data"][selected_subject]["raw_scores"], 1):
            print(f"  Test {i}: {score:.2f}%")

        test_num = int(input_scores("\nWhich test do you want to update? (1-4): ", min_val=1, max_val=4))
        obtained = input_scores("  Marks obtained: ", min_val=0.0, max_val=1000.0)
        total = input_scores("  Total possible marks: ", min_val=0.1, max_val=1000.0)

        new_percentage = (obtained / total) * 100
        data["pa_data"][selected_subject]["raw_scores"][test_num - 1] = new_percentage
        
        raw_list = data["pa_data"][selected_subject]["raw_scores"]
        data["pa_data"][selected_subject]["average"] = sum(raw_list) / len(raw_list)
        
        save_data(data)
        print(f"\n[✓] Updated {selected_subject} Test {test_num} to {new_percentage:.2f}%. New PA Avg: {data['pa_data'][selected_subject]['average']:.2f}%\n")

    elif up_choice == "2":
        new_score = input_scores(f"Enter new Terminal Exam percentage for {selected_subject} (0-100%): ", min_val=0.0, max_val=100.0)
        data["term_data"][selected_subject] = new_score
        save_data(data)
        print(f"\n[✓] Updated {selected_subject} Terminal Exam to {new_score:.2f}%\n")

def calculate_overall(data):
    """Outputs overall report."""
    if not data["pa_data"] or not data["term_data"]:
        print("\n[!] Error: You must complete BOTH Personal Assessment and Terminal Examination entries first.")
        return

    print("\n" + "=" * 70)
    print("                    FINAL OVERALL ACADEMIC REPORT                    ")
    print("=" * 70)
    print(f"{'Subject':<23} | {'PA (40%)':<9} | {'Term (60%)':<10} | {'Overall':<8} | {'Grade'}")
    print("-" * 70)

    for subject in data["subjects"]:
        pa_score = data["pa_data"].get(subject, {}).get("average", 0.0)
        term_score = data["term_data"].get(subject, 0.0)
        
        overall_score = (pa_score * 0.40) + (term_score * 0.60)
        letter_grade = get_as_letter_grade(subject, overall_score, data["thresholds"])

        print(f"{subject:<23} | {pa_score:>7.2f}% | {term_score:>8.2f}% | {overall_score:>6.2f}% | {letter_grade}")

    print("=" * 70 + "\n")

def main():
    data = load_data()

    if not data["subjects"]:
        setup_subjects(data)

    while True:
        print("=" * 45)
        print("  AS LEVEL GRADE TRACKING SYSTEM")
        print("=" * 45)
        print("1. Input All Personal Assessment Scores")
        print("2. Input All Terminal Examination Scores")
        print("3. Update Specific Test/Exam Score")
        print("4. View Overall Final Report")
        print("5. Reset & Reconfigure Subjects")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()

        if choice == "1":
            enter_personal_assessment(data)
        elif choice == "2":
            enter_terminal_exam(data)
        elif choice == "3":
            update_marks(data)
        elif choice == "4":
            calculate_overall(data)
        elif choice == "5":
            setup_subjects(data)
        elif choice == "6":
            print("\nExiting grade tracking system. Data saved automatically!")
            break
        else:
            print("\n[!] Invalid option. Select 1 to 6.\n")

if __name__ == "__main__":
    main()

