# Krellbot Community Packs

Community pack. Unverified. No guarantee.

This library is unpaid, unverified, and not a promise of profit. Packs here are
submitted by community members and have not been audited. Running any pack can
lose money. Nothing in this repository is financial advice.

## What this is

A community-contributed index of strategy packs for
[krellbot](https://github.com/d4rk-pri0r/krellbot). Each pack is a JSON file
that describes a trading strategy: indicators, entry/exit rules, risk limits,
and markets.

## How packs are organized

- `packs/` contains one JSON file per pack.
- `index.json` is the generated catalog. Do not edit it by hand. Regenerate
  it with `python3 scripts/build_index.py`.

Each pack is validated by `krellbot lint` on every pull request.

## Contributing

Open a pull request that adds a JSON file under `packs/`. The CI will run
`krellbot lint` against your changes.

## License

See the upstream krellbot project for license terms. Community contributions
follow the same terms as the rest of this repository.
