#include <iostream>
#include <string>

using namespace std;

int get_server_section() {
    string section = "# Server\r\nredis_version:{}\r\nredis_git_sha1:00000000\r\nredis_git_dirty:0\r\nredis_build_id:d81bff71cbf150e\r\nredis_mode:standalone\r\nos:{}\r\narch_bits:{}\r\nmonotonic_clock:POSIX clock_gettime\r\nmultiplexing_api:epoll\r\natomicvar_api:c11-builtin\r\ngcc_version:Python {}\r\nprocess_id:{}\r\nprocess_supervised:no\r\nrun_id:0\r\ntcp_port:{}\r\nserver_time_usec:{}\r\nuptime_in_seconds:{}\r\nuptime_in_days:{}\r\nhz:10\r\nconfigured_hz:10\r\nlru_clock:0\r\nexecutable:{}\r\nconfig_file:\r\nio_threads_active:";
    cout << section << "\r\n\r\n";
    return section.length();
}

int get_clients_section() {
    string section = "# Clients\r\nconnected_clients:{}\r\ncluster_connections:0\r\nmaxclients:10000\r\nclient_recent_max_input_buffer:0\r\nclient_recent_max_output_buffer:0\r\nblocked_clients:0\r\ntracking_clients:0\r\nclients_in_timeout_table:0";
    cout << section << "\r\n\r\n";
    return section.length();
}

int get_memory_section() {
    string section = "# Memory\r\nused_memory:{}\r\nused_memory_human:{}K\r\nused_memory_rss:{}\r\nused_memory_rss_human:{}M\r\nused_memory_peak:{}\r\nused_memory_peak_human:{}M\r\nused_memory_peak_perc:{}%\r\nused_memory_overhead:{}\r\nused_memory_startup:{}";
    cout << section << "\r\n\r\n";
    return section.length();
}

void get_all_sections() {
    int server = get_server_section();
    int clients = get_clients_section();
    int memory = get_memory_section();
    cout << (server + clients + memory) << endl << endl;
}

int main() {
    get_all_sections();
    return 0;
}
