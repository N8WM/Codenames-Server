import os
import json
import requests
from scipy.spatial.distance import cosine
from players.codemaster import Codemaster
from itertools import combinations

class ADACodemaster(Codemaster):
    """# Still a work in progress"""
    def __init__(self, **kwargs):
        super().__init__()
        self.team = kwargs.get("team", "Red")
        self.distance_threshold = kwargs.get("distance_threshold", 0.15)
        self.max_words_per_clue = kwargs.get("max_words_per_clue", 3)
        self.same_clue_patience = kwargs.get("sameCluePatience", 25)
        self.embeddings_file = "players/ada_embeddings.txt"
        self.api_key_file = "players/openai_api.key"
        self.wordlist_file = "players/cm_wordlist.txt"
        self.codenames_words = "game_wordpool.txt"
        self.model = "text-embedding-ada-002"
        self.embeddings = self.load_embeddings()
        self.past_clues = []

    def set_game_state(self, words_on_board, key_grid):
        self.words_on_board = words_on_board
        self.key_grid = key_grid

    def load_embeddings(self):
        if os.path.exists(self.embeddings_file):
            with open(self.embeddings_file, "r") as f:
                embeddings = json.load(f)
        else:
            with open(self.wordlist_file, "r") as f:
                words = f.read().splitlines()
            with open(self.codenames_words, "r") as f:
                words += [w.lower() for w in f.read().splitlines()]
            embeddings = self.get_embeddings(words)
            with open(self.embeddings_file, "w") as f:
                json.dump(embeddings, f)
        return embeddings

    def get_embeddings(self, words):
        with open(self.api_key_file, "r") as f:
            api_key = f.read().strip()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        chunk_size = 1000
        word_chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        embeddings = {}

        for chunk in word_chunks:
            data = {
                "model": self.model,
                "input": chunk
            }
            response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()
            chunk_embeddings = {word: embedding["embedding"] for word, embedding in zip(chunk, response_json["data"])}
            embeddings.update(chunk_embeddings)

        return embeddings

    def get_clue(self):
        GOOD_WORD_WEIGHT = 1
        BAD_WORD_WEIGHT = -self.max_words_per_clue
        CIVILIAN_WEIGHT = -2
        ASSASSIN_WEIGHT = -100

        team_words = [word.lower() for word, key in zip(self.words_on_board, self.key_grid) if key.lower() == self.team.lower() and "*" not in word]
        enemy_words = [word.lower() for word, key in zip(self.words_on_board, self.key_grid) if key.lower() == ("red" if self.team.lower() == "blue" else "blue") and "*" not in word]
        civilian_words = [word.lower() for word, key in zip(self.words_on_board, self.key_grid) if key.lower() == "civilian" and "*" not in word]
        assassin_words = [word.lower() for word, key in zip(self.words_on_board, self.key_grid) if key.lower() == "assassin" and "*" not in word]
        team_word_sequences = sum([list(combinations(team_words, i)) for i in range(1, self.max_words_per_clue + 1)], [])
        best_clues = []

        # with open("players/ada_clues.txt", "w") as f:
        #     f.write(f"Team words: {team_words}\n")
        #     f.write(f"Enemy words: {enemy_words}\n")
        #     f.write(f"Civilian words: {civilian_words}\n")
        #     f.write(f"Assassin words: {assassin_words}\n")
        #     f.write(f"Team word sequences: {team_word_sequences}\n\n\n")

        for word, embedding in self.embeddings.items():
            if word.lower() in [w.lower() for w in self.words_on_board]:
                continue
            enemy_word_distances = [cosine(embedding, self.embeddings[w]) for w in enemy_words]
            civilian_word_distances = [cosine(embedding, self.embeddings[w]) for w in civilian_words]
            assassin_word_distances = [cosine(embedding, self.embeddings[w]) for w in assassin_words]
            # with open("players/ada_clues.txt", "a") as f:
            #     f.write(f"Word: {word}\n")
            #     f.write(f"Enemy word distances: {enemy_word_distances}\n")
            #     f.write(f"Civilian word distances: {civilian_word_distances}\n")
            #     f.write(f"Assassin word distances: {assassin_word_distances}\n")
            for sequence in team_word_sequences:
                clue_score = 0
                team_word_distances = [cosine(embedding, self.embeddings[w]) for w in sequence]
                # if max(team_word_distances) <= self.distance_threshold:
                #     clue_score += GOOD_WORD_WEIGHT * len(sequence)
                clue_score += sum([GOOD_WORD_WEIGHT * (1 - d) for d in team_word_distances])
                # if min(enemy_word_distances) <= self.distance_threshold:
                #     clue_score += BAD_WORD_WEIGHT * len(enemy_words)
                clue_score += sum([BAD_WORD_WEIGHT * (1 - d) for d in enemy_word_distances])
                # if min(civilian_word_distances) <= self.distance_threshold:
                #     clue_score += CIVILIAN_WEIGHT * len(civilian_words)
                clue_score += sum([CIVILIAN_WEIGHT * (1 - d) for d in civilian_word_distances])
                # if min(assassin_word_distances) <= self.distance_threshold:
                #     clue_score += ASSASSIN_WEIGHT * len(assassin_words)
                clue_score += sum([ASSASSIN_WEIGHT * (1 - d) for d in assassin_word_distances])
                best_clues.append((word, clue_score, sequence, len(sequence)))
                # with open("players/ada_clues.txt", "a") as f:
                #     f.write(f"Sequence: {sequence}\n")
                #     f.write(f"Clue score: {clue_score}\n")
                
            # with open("players/ada_clues.txt", "a") as f:
            #     f.write("\n\n")

        best_clues.sort(key=lambda x: x[1], reverse=True)
        best_clue = best_clues.pop(0)
        while self.past_clues.count(best_clue[0]) > self.same_clue_patience:
            best_clue = best_clues.pop(0)
        self.past_clues.append(best_clue[0])
        return best_clue[0], best_clue[3]
