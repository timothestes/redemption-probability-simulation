install-deps:
	source config.sh
run:
	python3 -m src.main \
		--n_simulations 10000000 \
		--deck_size 50 \
		--n_tutors_to_try 0 1 2 3 4 5 6 7 8 9 10 \
		--n_cycler_souls_to_try 0 1 2 \
		--going_first \
		--summarize_results
run-spectrograph:
	python3 -m src.spectrograph \
		--n_simulations 1000000 \
		--deck_file_path decks/test_dummy_deck.txt \
		--cycler_logic random \
		--account_for_crowds
plot:
	python3 -m src.visualization
test:
	pytest