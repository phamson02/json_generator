def escape_json_string(json_string):

    json_string = (
        json_string.replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .replace("  ", "")
        .replace(": [", ":[")
        .replace('", "', '","')
        .replace('], "', '],"')
    )

    input_json = json_string

    # Start and end patterns for JSON string delimiters
    start_patterns = ['["', '{"', ': "', '","', '],"']
    end_patterns = ['"]', '"}', '","', '":']

    # Tracking whether we are inside a JSON string
    in_string = False
    # Result container
    result = []
    # Iterate through the string by index and character
    i = 0
    while i < len(input_json):
        char = input_json[i]

        # Detect entering a JSON string
        if char == '"' and not in_string:
            # Check the previous characters for start pattern
            prev_seq = input_json[
                max(0, i - 2) : i + 1
            ]  # Look two characters back and one ahead

            if any(prev_seq.endswith(pat) for pat in start_patterns):
                # We are at a legitimate start of a JSON string
                result.append(char)
                in_string = True
            else:
                # It's a quote that should be escaped
                result.append('\\"')
        elif char == '"' and in_string:
            # Check if we are at the end of a JSON string
            next_seq = input_json[
                i : i + 3
            ]  # We need to check the next characters for end pattern
            if any(next_seq.startswith(pat) for pat in end_patterns):
                # It's a legitimate end of a JSON string
                result.append(char)
                in_string = False
            else:
                # It's a quote that should be escaped inside a string
                result.append('\\"')
        else:
            # Add the character as is
            result.append(char)

        i += 1

    return "".join(result)
