import argparse
from algoz.search import breadth_first
from algoz.search import depth_first
from algoz.search import binary



def main():
    # arg parser
    parser = argparse.ArgumentParser(description="Search for word in file")

    # word
    parser.add_argument("-w", "--word", required=True, help="Word to be searched for")

    # file
    parser.add_argument("-f", "--file", required=True, help="Path to file that is to be searched")
    
    # algorithm
    parser.add_argument("-sa", "--search-algorithm", choices=["binary-search", "depth-first-search", "breadth-first-search"], required=True, help="The algorithm to be used to search the file")
    
    # order
    parser.add_argument("-o", "--order", choices=["pre-order", "post-order", "in-order", "level-order"], required=True, help="The order in which to traverse the tree")
    
    # all args
    args = parser.parse_args()
    
    # depth first search
    if args.search_algorithm == "depth-first-search":
        # create a depth_first module with a search function containing algorithm code
        depth_first.search(args)
        return

    # breadth first search
    if args.search_algorithm == "breadth-first-search":
        # create a breadth_first module with a search function containing algorithm code
        breadth_first.search(args)
        return

    # binary search
    if args.search_algorithm == "binary-search":
        # create a binary module with a search function containing algorithm code
        binary.search(args)
        return


if __name__ == "__main__":
    main()
