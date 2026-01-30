import os

def load_ai_context(directory=".ai"):
    """
    Reads all markdown files in the specified directory and returns their content
    formatted for AI context injection.
    """
    context_data = []
    
    if not os.path.exists(directory):
        return "No .ai directory found."

    print(f"Loading context from {directory}...\n")

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    context_data.append(f"--- START FILE: {filename} ---\n{content}\n--- END FILE: {filename} ---\n")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    return "\n".join(context_data)

if __name__ == "__main__":
    # Get the absolute path to the .ai directory
    # Assuming this script is in .ai/scripts/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir) # Go up one level to .ai
    
    full_context = load_ai_context(root_dir)
    print(full_context)
    
    # Optional: Save to a single file for easy copy-pasting
    # with open("full_ai_context.txt", "w", encoding="utf-8") as f:
    #     f.write(full_context)
