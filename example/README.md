# Example

This is a simple AltWalker example project used for debugging and demonstration purposes.

## Checking the Model

To check the model, use the following command:

```bash
altwalker check -m models/model.json "random(vertex_coverage(100))"
```

## Verify the Code

To verify the code against the model, execute:

```bash
altwalker verify -m models/model.json tests
```

## Running Tests

### Offline

To run tests in offline mode, use the following command:

```bash
altwalker walk tests steps/full-vertex-coverage.json
```

### Online

For online mode testing, execute the command below:

```bash
altwalker online tests -m models/model.json "random(vertex_coverage(100))"
```
