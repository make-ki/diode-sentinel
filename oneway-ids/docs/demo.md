# Paced synthetic demo

Run `./demo.sh` for a fresh synthetic capture streamed through the normal
`run.py --pipe` live path. The dashboard starts before the pipeline, then
updates as alerts arrive. At EOF the completed view stays open until Ctrl-C.
The default speed is 10 simulated seconds per wall second (about one minute
for the 600 second capture); use `./demo.sh --speed=25` to shorten the replay,
or `--port=8601` if port 8600 is occupied.

Each invocation generates directly into a new temporary directory and places
its FIFO, alert log and sidecars there. It does not reuse `traffic.pcap` or
load a prior JA4 inventory. The generated capture is synthetic and includes
seeded threat fixtures such as malware JA4 fingerprints; the dashboard marks
it as demonstration data. The default pipeline is rules plus the DGA CNN.
The LightGBM flow scorer and category 5-7 models are experimental options and
are omitted from this demo.

The automated live-update smoke check is opt-in because it generates and
streams a full capture. Run it with
`DIODESENTINEL_DEMO_SMOKE=1 .venv/bin/python tests/test_demo_smoke.py` (after
the normal loader setup). It verifies an alert appears while both pipeline and
replay writer are still running, then sends Ctrl-C and checks that the child
processes, dashboard and temporary files are removed. A separate normal run
through EOF leaves the completed dashboard available until Ctrl-C.
