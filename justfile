install-deps:
	source config.sh
run:
	python3 -m src.main \
		--n_simulations 50000 \
		--deck_sizes_to_try 50 \
		--n_cycler_souls_to_try 0 1 2 \
		--going_first \
		--include_hopper \
		--generate_plot
test:
	pytest