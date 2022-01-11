import sys

def print_progress_bar(i, maximum, post_text):
    n_bar=20 
    j = i/maximum
    sys.stdout.write('\r')
    sys.stdout.write(f"[{'#' * int(n_bar * j):{n_bar}s}] {int(100 * j)}% {post_text}")
    sys.stdout.flush()
