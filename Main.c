#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <time.h>

#define BUFFER_SIZE 8000
#define PACKET_CONTENT "UDP traffic test"

void send_udp_traffic(int sockfd, struct sockaddr_in *dest_addr, int duration_seconds) {
    char buffer[BUFFER_SIZE];
    snprintf(buffer, sizeof(buffer), "%s", PACKET_CONTENT);
    
    time_t start_time = time(NULL);
    while (difftime(time(NULL), start_time) < duration_seconds) {
        ssize_t sent_len = sendto(sockfd, buffer, strlen(buffer), 0, 
                                  (struct sockaddr *)dest_addr, sizeof(*dest_addr));
        if (sent_len < 0) {
            perror("sendto failed");
            return;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <target_ip> <target_port> <duration>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    const char *target_ip = argv[1];
    int target_port = atoi(argv[2]);
    int duration = atoi(argv[3]);

    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in dest_addr;
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(target_port);

    if (inet_pton(AF_INET, target_ip, &dest_addr.sin_addr) <= 0) {
        fprintf(stderr, "Invalid address or address not supported\n");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    send_udp_traffic(sockfd, &dest_addr, duration);

    close(sockfd);
    return 0;
}
