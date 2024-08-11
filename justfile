install-deps:
	source config.sh
run:
	python3 -m src.main_v2 \
		--n_simulations 500000 \
		--deck_file_path decks/test_dummy_deck.txt \
		--cycler_logic random \
		--crowds_ineffectiveness_weight .6 \
		--matthew_fizzle_rate .15
test:
	pytest