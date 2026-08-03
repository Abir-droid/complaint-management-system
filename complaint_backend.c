#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_COMPLAINTS 100
#define DATA_FILE "complaints.txt"

typedef struct {
    int  id;
    char name[50];
    char phone[20];
    char category[30];
    char description[100];
    char status[20];
    char assignedTeam[30];
} Complaint;

Complaint complaints[MAX_COMPLAINTS];
int complaintCount = 0;
int nextId = 1;

/* Phone number validation helper from original code */
int isValidPhone(const char *phone) {
    int len = strlen(phone);
    if (len < 7 || len > 15) return 0;
    for (int i = 0; i < len; i++) {
        if (phone[i] < '0' || phone[i] > '9') return 0;
    }
    return 1;
}

void loadComplaints(void) {
    FILE *fp = fopen(DATA_FILE, "r");
    complaintCount = 0;
    nextId = 1;
    if (fp == NULL) return;

    while (complaintCount < MAX_COMPLAINTS &&
           fscanf(fp, "%d|%49[^|]|%19[^|]|%29[^|]|%99[^|]|%19[^|]|%29[^\n]\n",
                  &complaints[complaintCount].id,
                  complaints[complaintCount].name,
                  complaints[complaintCount].phone,
                  complaints[complaintCount].category,
                  complaints[complaintCount].description,
                  complaints[complaintCount].status,
                  complaints[complaintCount].assignedTeam) == 7) {
        if (complaints[complaintCount].id >= nextId) nextId = complaints[complaintCount].id + 1;
        complaintCount++;
    }
    fclose(fp);
}

void saveComplaints(void) {
    FILE *fp = fopen(DATA_FILE, "w");
    if (fp == NULL) return;

    for (int i = 0; i < complaintCount; i++) {
        fprintf(fp, "%d|%s|%s|%s|%s|%s|%s\n",
                complaints[i].id, complaints[i].name, complaints[i].phone,
                complaints[i].category, complaints[i].description,
                complaints[i].status, complaints[i].assignedTeam);
    }
    fclose(fp);
}

int add_complaint(const char *name, const char *phone, const char *category, const char *description) {
    loadComplaints();
    if (complaintCount >= MAX_COMPLAINTS) return -1;
    
    // Validate phone number before saving!
    if (!isValidPhone(phone)) {
        return -2; // Return error code -2 for invalid phone
    }

    Complaint c;
    c.id = nextId++;
    strncpy(c.name, name, sizeof(c.name) - 1);
    c.name[sizeof(c.name) - 1] = '\0';
    
    strncpy(c.phone, phone, sizeof(c.phone) - 1);
    c.phone[sizeof(c.phone) - 1] = '\0';
    
    strncpy(c.category, category, sizeof(c.category) - 1);
    c.category[sizeof(c.category) - 1] = '\0';
    
    strncpy(c.description, description, sizeof(c.description) - 1);
    c.description[sizeof(c.description) - 1] = '\0';
    
    strcpy(c.status, "Pending");
    strcpy(c.assignedTeam, "Not Assigned");

    complaints[complaintCount++] = c;
    saveComplaints();
    return c.id;
}

int update_complaint_admin(int id, const char *status, const char *team) {
    loadComplaints();
    for (int i = 0; i < complaintCount; i++) {
        if (complaints[i].id == id) {
            if (status && strlen(status) > 0) {
                strncpy(complaints[i].status, status, sizeof(complaints[i].status) - 1);
            }
            if (team && strlen(team) > 0) {
                strncpy(complaints[i].assignedTeam, team, sizeof(complaints[i].assignedTeam) - 1);
            }
            saveComplaints();
            return 1;
        }
    }
    return 0;
}

int delete_complaint(int id) {
    loadComplaints();
    int found = -1;
    for (int i = 0; i < complaintCount; i++) {
        if (complaints[i].id == id) {
            found = i;
            break;
        }
    }
    if (found != -1) {
        for (int i = found; i < complaintCount - 1; i++) {
            complaints[i] = complaints[i + 1];
        }
        complaintCount--;
        saveComplaints();
        return 1;
    }
    return 0;
}