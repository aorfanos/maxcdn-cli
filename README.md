# maxcdn-cli
A CLI tool to interact with MaxCDN's API.

## USAGE

### Installation

1. Create an app in MaxCDNs panel
2. Whitelist your IP

### Examples

- Create a zone
```
maxcdn-cli zone add ZONENAME ORIGIN-URL
```

- Create zone with custom domain and enable 5 locations
```
maxcdn-cli zone add ZONENAME ORIGIN-URL --customDomain="https://cdn.test.com" --enableFlex
```

- Purge CDN cache for a zone
```
maxcdn-cli cache purge ZONE-ID #also: {--silent. --prettyPrint}
```

- Add a custom domain
```
maxcdn-cli domain add ZONE-ID DOMAIN
```

You get the feeling. As of yet, the structure (and functionalities available are):

- maxcdn-cli
  - zone
    - add
    - delete
    - flex
    - info
    - list
    - update
  - account
    - info
  - cache
    - purge
  - domain
    - add
    - delete
  - ssl
    - add
    - list

