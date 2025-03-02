from agent import ColdCallAgent

def main():
    agent = ColdCallAgent()
    
    while True:
        print("\nChoose scenario:")
        print("1. ERP Demo Scheduling")
        print("2. Candidate Interview")
        print("3. Payment Follow-up")
        print("4. Exit")
        
        choice = input("Enter choice (1-4): ")
        
        if choice == "1":
            agent.handle_scenario("demo")
        elif choice == "2":
            agent.handle_scenario("interview")
        elif choice == "3":
            agent.handle_scenario("payment")
        elif choice == "4":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()