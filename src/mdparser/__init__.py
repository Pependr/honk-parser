import argparse


def main() -> None:
	parser = argparse.ArgumentParser(
		prog="mdparser",
		description="A tool that parses your data to beautiful markdowns",
	)

	parser.add_argument("path")

	args = parser.parse_args()
	print(args.path)


if __name__ == "__main__":
	main()
