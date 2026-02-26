import matplotlib.pyplot as plt
import string

def preprocess_text(filename):
    """
    Reads the file, converts to lowercase, removes punctuation,
    and returns a list of words.
    """
    words = []
    # TODO: Open file, read text, lower(), remove punctuation, split into words
    with open(filename,'r') as f:
        words = f.read().lower()
        for ch in string.punctuation:
                words = words.replace(ch,"")
        words = words.split()
    return words

def count_ngrams(words, n):
    """
    Generates n-grams from the list of words.
    Returns a dictionary:
      - For n=1: Key is string (word)
      - For n>1: Key is tuple of strings (word1, word2, ...)
    """
    counts = {}
    for i in range(len(words) - n + 1):
            ngram = words[i:i+n]
            if n==1 :
                key = ngram[0]
            else :
                key = tuple(ngram)
            counts[key] = counts.get(key, 0) + 1
    
    # TODO: Iterate through words to generate n-grams and count frequencies
    
    return counts

def save_sorted_ngrams(ngram_dict, output_file):
    """
    Sorts the dictionary by Frequency (Descending) then Lexicographical (Ascending).
    Writes to output_file in format: word \t count
    """
    # TODO: Sort the items. Hint: use key=lambda x: (-x[1], x[0])
    sorted_items = sorted(ngram_dict.items(), key=lambda x: (-x[1], x[0]))
    
    # TODO: Write to file. 
    # Note: For n > 1, join the tuple keys with a space before writing.
    with open(output_file, "w") as f:
        for key, freq in sorted_items:
            if isinstance(key, tuple):
                word = " ".join(key)
            else:
                word = key
            f.write(f"{word}\t{freq}\n")

def plot_frequency_vs_rank(ngram_dict, filename):
    """
    Generates a Frequency vs Rank graph (Zipf's Law visualization).
    Saves the plot to the specified filename.
    """
    if not ngram_dict:
        return

    # TODO: Sort frequencies in descending order
    # frequencies = ...
    frequencies = sorted(ngram_dict.values(), reverse=True)
    
    # TODO: Generate Ranks (1 to N)
    ranks = range(1, len(frequencies) + 1)
    
    # TODO: Plot Rank vs Frequency
    plt.figure(figsize=(10, 6))
    
    # Using Log-Log plot usually best for word frequency data (Zipf's law)
    plt.loglog(ranks, frequencies, marker='.', linestyle='none', markersize=2)
    
    plt.title(f'Frequency vs Rank ({filename})')
    plt.xlabel('Rank (log)')
    plt.ylabel('Frequency (log)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Saved plot: {filename}")

def main():
    input_file = 'felicity_work.txt'
    
    # --- 1. Preprocessing ---
    words = preprocess_text(input_file)
    
    # --- 2. Analysis (Generate Dictionaries) ---
    # Variable names must be exactly klk1, klk2, klk3
    klk1 = count_ngrams(words, 1)
    klk2 = count_ngrams(words, 2)
    klk3 = count_ngrams(words, 3)
    
    # --- 3. Export Sorted Counts ---
    # Write to 1.txt, 2.txt, 3.txt
    if klk1: save_sorted_ngrams(klk1, '1.txt')
    if klk2: save_sorted_ngrams(klk2, '2.txt')
    if klk3: save_sorted_ngrams(klk3, '3.txt')
    
    # --- 4. Visualization (Frequency vs Rank) ---
    if klk1: plot_frequency_vs_rank(klk1, '1.png')
    if klk2: plot_frequency_vs_rank(klk2, '2.png')
    if klk3: plot_frequency_vs_rank(klk3, '3.png')
    
    # --- 5. Stdout Analysis ---
    
    # Line 1: Top 3 most frequent unigrams
    # TODO: Get top 3 from klk1
    top_3_unigrams = sorted(klk1.items(), key=lambda x: (-x[1], x[0]))[:3]
    formatted_top3 = ", ".join([f"{w}:{c}" for w, c in top_3_unigrams])
    print(formatted_top3)
    
    # Line 2: Most frequent bigram starting with "fest"
    # TODO: Filter klk2 for keys starting with 'fest', find max
    fest_bigrams = [k for k in klk2 if k[0]=="fest"]
    best_fest_bigram = None
    if fest_bigrams:
        best_fest_bigram = max(fest_bigrams, key=lambda k:(klk2[k], tuple([-ord(c) for c in k[1]])))
        
    # Line 3: Count of the trigram ('fest', 'starts', 'now')
    # TODO: Fetch count from klk3
    target_trigram = ('fest', 'starts', 'now')
    trigram_count = klk3.get(target_trigram, 0)
    print(trigram_count)

if __name__ == "__main__":
    main()