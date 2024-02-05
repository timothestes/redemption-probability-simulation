install-deps:
	source config.sh

run:
	python3 -m src.main \
		--n_simulations 1000000 \
		--deck_sizes_to_try 50 \
		--n_cycler_souls_to_try 0 1 2 \
		--virgin_birth \
		--generate_plot
test:
	pytest