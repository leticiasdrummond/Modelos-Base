.PHONY: run-base run-mod run-all

run-base:
	python src/run_scenario.py --config configs/caso_base.yaml --output results/caso_base

run-mod:
	python src/run_scenario.py --config configs/caso_modificado.yaml --output results/caso_modificado

run-all: run-base run-mod
