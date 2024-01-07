# Python implementation of a randomly generated BIP-39 seed phrase
# Note: You should NOT generate your seed phrase on an internet-connected computer!!!

import hashlib, secrets

bip39 = []
startIdx = 0
bipDict = {}

with open('english.txt') as f:
  for line in f:
    bip39.append(line.strip())

for i in range(1, 5):
  for j in range(1, 5):
    for k in range(1, 5):
      for l in range(1, 5):
        bipDict[f"{i}{j}{k}{l}"] = bip39[startIdx:(startIdx + 8)]
        startIdx += 8

def roll():
  output = []
  while len(output) < 5:
    currRoll = secrets.randbelow(6) + 1 # Effectively a range of 1-6

    if currRoll < 5:
      output.append(str(currRoll))

  output.append(secrets.choice(["heads", "tails"]))
  return output

# Generate first 23 words of a seedphrase and return.  In BIP-39, 24th word is a pseudo-checksum.
def twentyThreeWords():
  seedPhrase = []
  for x in range(23):
    wordRoll = roll()

    # Get first four dice rolls in string format: ''.join(wordRoll[:4])
    firstFour = ''.join(wordRoll[:4])

    wordRow = bipDict[firstFour]
    sliceRow = int(wordRoll[4]) - 1 # Adhere to 0-indexing
    coinFlip = wordRoll[5]

    # Change wordRow to nested lists with two elements each
    wordRow = [wordRow[i:i+2] for i in range(0, len(wordRow), 2)]
    wordChoice = wordRow[sliceRow][0] if coinFlip == 'heads' else wordRow[sliceRow][1]
    seedPhrase.append(wordChoice)

  seedPhrase.append('?')
  return seedPhrase

seedphrase = twentyThreeWords()

# Borrowed checksum logic from
# https://www.blockplate.com/blogs/blockplate/the-special-last-word-of-a-seed-phrase
# https://www.blockplate.com/blogs/blockplate/seed-phrase-recovery-tool-find-the-last-word-with-code

seed_phrase_index = [bip39.index(word) if word != "?" else word for word in seedphrase]

# converts seed_phrase_index (with numbers) to binary
seed_phrase_binary = [format(number, "011b") if number != "?" else number for number in seed_phrase_index]

# calculates the number of bits missing for entropy
num_missing_bits = int(11 - (1/3) * (len(seedphrase)))

# calculates all the possible permutation of missing bits for entropy
missing_bits_possible = [bin(x)[2:].rjust(num_missing_bits, "0") for x in range(2 ** num_missing_bits)]

# combines the binary representation of seed phrase with each possible missing bits to result in the possible entropy
entropy_possible = ["".join(seed_phrase_binary[:-1])+bits for bits in missing_bits_possible]

# inputs each entropy_possible in the SHA256 function to result in the corresponding checksum
checksum = [format(hashlib.sha256(int(entropy, 2).to_bytes(len(entropy) // 8, byteorder="big")).digest()[0], "08b")[:11-num_missing_bits] for entropy in entropy_possible]

# combines the missing bits with its corresponding checksum
last_word_bits = [i + j for i, j in zip(missing_bits_possible, checksum)]

# transforms 11 bit number to indexed number and then the corresponding word in the BIP39 wordlist
last_word = [bip39[int(bits, 2)] for bits in last_word_bits]

print("Randomly generated seed phrase:")
print()
print(' '.join(seedphrase[:-1]))
print()
print(f"Checksum word choice: {last_word}")