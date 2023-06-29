import string

def is_line_allowed(line):
    allowed_chars = string.ascii_letters + string.digits + string.punctuation + string.whitespace
    allowed_chars = allowed_chars[:-2]
    return all(char in allowed_chars for char in line)

def is_line_valid(line):
    return len(line.strip()) >= 100

def remove_unwanted_lines(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            if is_line_allowed(line) and is_line_valid(line):
                f_out.write(line)


if __name__ == "__main__":
    input_file = 'output/output2.txt'
    output_file = 'output/cleaned_output6.txt'
    remove_unwanted_lines(input_file, output_file)