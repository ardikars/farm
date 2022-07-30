
### Create docker bridge network

```bash
$ docker network create --driver bridge chia_network
```

### Create and run container

```bash
$ docker-compose -f chia.yml up -d
```
