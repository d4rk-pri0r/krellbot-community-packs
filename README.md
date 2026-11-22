# Krellbot Community Packs

Community pack. Unverified. No guarantee.

This library is unpaid, unverified, and not a promise of profit. Packs here are
submitted by community members and have not been audited. Running any pack can
lose money. Nothing in this repository is financial advice.

## What this is

A community-contributed index of strategy packs for
[krellbot](https://github.com/d4rkpr10r-Labs/krellbot). Each pack is a JSON file
that describes a trading strategy: indicators, entry/exit rules, risk limits,
and markets.

## How packs are organized

- `packs/` contains one JSON file per pack.
- `index.json` is the generated catalog. Do not edit it by hand. Regenerate
  it with `python3 scripts/build_index.py`.

CI verifies the generated index and validates every pack with Krellbot's
Pack DSL validator on pull requests and pushes to `main`. Pull requests
check the proposed files in the checkout. Pushes to `main` also check that
GitHub serves the same pack bytes at the pushed commit.

## Contributing

Add a JSON file under `packs/`, regenerate `index.json`, and open a pull
request. With Krellbot installed, run `python3 scripts/build_index.py --validate`
to check the full catalogue locally.

See the [community pack authoring checklist](https://github.com/d4rkpr10r-Labs/krellbot/blob/main/docs/community.md)
for the required fields, filename rules, and install size limit.

## License

See the upstream krellbot project for license terms. Community contributions
follow the same terms as the rest of this repository.
