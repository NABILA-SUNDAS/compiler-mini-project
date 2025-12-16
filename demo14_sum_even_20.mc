// sum of even numbers from 1 to 20
start
    int i = 1;
    int sum = 0;

    while (i <= 20) {
        if (i % 2 == 0) {
            sum = sum + i;
        }
        i = i + 1;
    }

    print(sum);
end
