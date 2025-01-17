PYTHON=python3
GENERATED_FILES=alg.*
NUM=5
OUTPUT_CHOMSKY=test_$(NUM)_chomsky.res
OUTPUT_GREIBACH=test_$(NUM)_greibach.res

all: run

run:
	$(PYTHON) grammaire.py

generer_chomsky: run
	$(PYTHON) generer.py alg.chomsky $(NUM) > $(OUTPUT_CHOMSKY)

generer_greibach: run
	$(PYTHON) generer.py alg.greibach $(NUM) > $(OUTPUT_GREIBACH)

diff: run generer_chomsky generer_greibach
	diff $(OUTPUT_CHOMSKY) $(OUTPUT_GREIBACH)

clean:
	rm -f $(GENERATED_FILES) $(OUTPUT_CHOMSKY) $(OUTPUT_GREIBACH)