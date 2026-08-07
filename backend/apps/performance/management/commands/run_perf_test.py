import json
from django.core.management.base import BaseCommand
from apps.performance.load_test import run_load_benchmark


class Command(BaseCommand):
    help = "Runs simulated enterprise load testing & performance benchmarking against cached endpoints."

    def add_arguments(self, parser):
        parser.add_argument(
            "--concurrency", type=int, default=25, help="Number of simulated concurrent request worker threads."
        )
        parser.add_argument(
            "--iterations", type=int, default=5, help="Number of loop iterations per worker thread."
        )

    def handle(self, *args, **options):
        concurrency = options["concurrency"]
        iterations = options["iterations"]
        self.stdout.write(self.style.NOTICE(f"Starting GrantLoop Enterprise Performance Benchmark (Concurrency={concurrency}, Iterations={iterations})..."))
        
        results = run_load_benchmark(concurrent_requests=concurrency, iterations_per_worker=iterations)
        
        self.stdout.write("\n=== BENCHMARK TELEMETRY RESULTS ===")
        self.stdout.write(json.dumps(results, indent=2))
        
        if results["status"] == "PASSED":
            self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Performance & Load benchmark passed without errors."))
        else:
            self.stdout.write(self.style.WARNING("\n[WARNING] Benchmark finished with degraded thresholds or errors."))
