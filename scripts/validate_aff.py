"""This was mostly made by chatgpt but of course i had to fix it because AI is stoopid."""
import sys
import re


def validate_hunspell_aff(file_content):
    lines = file_content.split('\n')
    valid = True
    errors = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("SFX") or line.startswith("PFX"):
            parts = line.split()
            if len(parts) >= 4 and parts[2] == 'Y':
                rule_count = int(parts[3])
                rule_type = parts[0]
                rule_name = parts[1]
                rule_lines = 0
                rule_start_line = i
                i += 1
                same_block_pattern = re.compile(f"{rule_type}\\s+{rule_name}")
                while i < len(lines) and same_block_pattern.search(lines[i]):
                    if not lines[i].strip().startswith("#"):
                        rule_lines += 1
                    i += 1

                if rule_lines != rule_count:
                    valid = False
                    errors.append(f"Rule {rule_type} {rule_name} at line {rule_start_line + 1}: "
                                  f"Expected {rule_count} rules, found {rule_lines}")
                continue
        i += 1

    return valid, errors


def validate_hunspell_aff_file(filepath):
    try:
        with open(filepath, 'r', encoding='latin-1') as file:
            file_content = file.read()
    except FileNotFoundError:
        return False, ["File not found."]
    except UnicodeDecodeError:
        return False, ["File encoding issue. Ensure the file is in LATIN-1 encoding."]
    except Exception as e:
        return False, [str(e)]
    return validate_hunspell_aff(file_content)


if __name__ == '__main__':
    print(validate_hunspell_aff_file(sys.argv[1]))
