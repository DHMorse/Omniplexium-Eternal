import math

def xpToLevel(experience, base=10):
    return int(math.log(experience + 1, base)) + 1

def main():
    print(xpToLevel(int(input())))

if __name__ == "__main__":
    main()