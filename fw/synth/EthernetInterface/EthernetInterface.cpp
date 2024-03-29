/* EthernetInterface.cpp */
/* Copyright (C) 2012 mbed.org, MIT License
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software
 * and associated documentation files (the "Software"), to deal in the Software without restriction,
 * including without limitation the rights to use, copy, modify, merge, publish, distribute,
 * sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or
 * substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
 * BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 * DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
#include "EthernetInterface.h"

#include "lwip/inet.h"
#include "lwip/netif.h"
#include "netif/etharp.h"
#include "lwip/dhcp.h"
#include "arch/lpc17_emac.h"
#include "lpc_phy.h"
#include "lwip/tcpip.h"

#include "mbed.h"

//Debug is disabled by default
#if 1
#define DBG(x, ...) std::printf("[NET : DBG]"x"\r\n", ##__VA_ARGS__); 
#define WARN(x, ...) std::printf("[NET : WARN]"x"\r\n", ##__VA_ARGS__); 
#define ERR(x, ...) std::printf("[NET : ERR]"x"\r\n", ##__VA_ARGS__); 
#else
#define DBG(x, ...) 
#define WARN(x, ...)
#define ERR(x, ...) 
#endif

#define INFO(x, ...) printf("[NET : INFO]"x"\r\n", ##__VA_ARGS__);

/* TCP/IP and Network Interface Initialisation */
static struct netif lpcNetif;

static char mac_addr[19];
static char ip_addr[17] = "\0";
static char gateway[17] = "\0";
static char networkmask[17] = "\0";
static bool use_dhcp = false;

static Semaphore tcpip_inited(0);
static Semaphore netif_linked(0);
static Semaphore netif_up(0);

static void tcpip_init_done(void *arg) {
    tcpip_inited.release();
}

static void netif_link_callback(struct netif *netif) {
    if (netif_is_link_up(netif)) {
        netif_linked.release();
    }
}

static void netif_status_callback(struct netif *netif) {
    if (netif_is_up(netif)) {
        strcpy(ip_addr, inet_ntoa(netif->ip_addr));
        strcpy(gateway, inet_ntoa(netif->gw));
        strcpy(networkmask, inet_ntoa(netif->netmask));
        netif_up.release();
    }
}

static void init_netif(ip_addr_t *ipaddr, ip_addr_t *netmask, ip_addr_t *gw) {
    DBG("Before tcpip_init");
    tcpip_init(tcpip_init_done, NULL);
    DBG("After tcpip_init");
    DBG("Before tcpip_inited.wait");
    tcpip_inited.wait();
    DBG("After tcpip_inited.wait");
    
    memset((void*) &lpcNetif, 0, sizeof(lpcNetif));
    
    DBG("Before netif_add");
    netif_add(&lpcNetif, ipaddr, netmask, gw, NULL, lpc_enetif_init, tcpip_input);
    DBG("After netif_add");
    
    DBG("Before netif_set_default");
    netif_set_default(&lpcNetif);
    DBG("After netif_set_default");
    
    DBG("Before netif_set_link_callback");
    netif_set_link_callback  (&lpcNetif, netif_link_callback);
    DBG("After netif_set_link_callback");
    DBG("Before netif_set_status_callback");
    netif_set_status_callback(&lpcNetif, netif_status_callback);
    DBG("After netif_set_status_callback");
}

static void set_mac_address(void) {
    DBG("In set_mac_address");
#if (MBED_MAC_ADDRESS_SUM != MBED_MAC_ADDR_INTERFACE)
    snprintf(mac_addr, 19, "%02x:%02x:%02x:%02x:%02x:%02x", MBED_MAC_ADDR_0, MBED_MAC_ADDR_1, MBED_MAC_ADDR_2,
             MBED_MAC_ADDR_3, MBED_MAC_ADDR_4, MBED_MAC_ADDR_5);
#else
    char mac[6];
    DBG("Before mbed_mac_address");
    mbed_mac_address(mac);
    DBG("After mbed_mac_address");
    snprintf(mac_addr, 19, "%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    DBG("%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
#endif
}

int EthernetInterface::init() {
    use_dhcp = true;
    DBG("Init DHCP");
    set_mac_address();
    DBG("After set_mac_address");
    DBG("Before init_netif");
    init_netif(NULL, NULL, NULL);
    DBG("After init_netif");
    return 0;
}

int EthernetInterface::init(const char* ip, const char* mask, const char* gateway) {
    DBG("Init static");
    use_dhcp = false;
    
    DBG("Set MAC Address");
    set_mac_address();
    
    strcpy(ip_addr, ip);
    
    ip_addr_t ip_n, mask_n, gateway_n;
    
    DBG("inet_aton");
    inet_aton(ip, &ip_n);
    inet_aton(mask, &mask_n);
    inet_aton(gateway, &gateway_n);
    DBG("init_netif");
    init_netif(&ip_n, &mask_n, &gateway_n);
    
    return 0;
}

int EthernetInterface::connect(unsigned int timeout_ms) {
    NVIC_SetPriority(ENET_IRQn, ((0x01 << 3) | 0x01));
    NVIC_EnableIRQ(ENET_IRQn);
    
    int inited;
    if (use_dhcp) {
        DBG("dhcp_start");
        dhcp_start(&lpcNetif);
        
        // Wait for an IP Address
        // -1: error, 0: timeout
        DBG("wait for ip");
        inited = netif_up.wait(timeout_ms);
    } else {
        DBG("netif_set_up");
        netif_set_up(&lpcNetif);
        
        // Wait for the link up
        DBG("wait for link");
        inited = netif_linked.wait(timeout_ms);
    }
    
    return (inited > 0) ? (0) : (-1);
}

int EthernetInterface::disconnect() {
    if (use_dhcp) {
        dhcp_release(&lpcNetif);
        dhcp_stop(&lpcNetif);
    } else {
        netif_set_down(&lpcNetif);
    }
    
    NVIC_DisableIRQ(ENET_IRQn);
    
    return 0;
}

char* EthernetInterface::getMACAddress() {
    return mac_addr;
}

char* EthernetInterface::getIPAddress() {
    return ip_addr;
}

char* EthernetInterface::getGateway() {
    return gateway;
}

char* EthernetInterface::getNetworkMask() {
    return networkmask;
}


