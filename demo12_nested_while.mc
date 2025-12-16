// nested while loops (simple pattern)
start
    int i = 1;
    int j = 1;

    while (i <= 3) {
        j = 1;
        while (j <= 2) {
            print(i * 10 + j);
            j = j + 1;
        }
        i = i + 1;
    }
end
