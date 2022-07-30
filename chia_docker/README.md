
### Migration

```bash
$ docker-compose -f chia.yml up -d
$ docker container exec -it chia-farmer /bin/bash
```

Edit pool config in `$CHIA_ROOT/config/config.yaml`.

```
pool:
  logging: *id001
  network_overrides: *id002
  pool_list:
  - authentication_public_key: ..
    launcher_id: '0x..'
    owner_public_key: '0x..'
    p2_singleton_puzzle_hash: '0x..'
    payout_instructions: ..
    pool_url: https://your.pool.com
    target_puzzle_hash: '0x..'
  selected_network: mainnet
  xch_target_address: xch1..
```
