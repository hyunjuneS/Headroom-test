"""Scenario 8: config file - a long Kubernetes-style YAML."""

from _common import main


def build():
    services = []
    for i in range(30):
        replicas = 0 if i == 19 else 3
        services.append(
            f"- name: service-{i}\n"
            f"  image: registry.example.com/service-{i}:1.4.{i}\n"
            f"  replicas: {replicas}\n"
            f"  resources:\n    limits:\n      cpu: 500m\n      memory: 512Mi\n"
            f"  env:\n    - name: LOG_LEVEL\n      value: info\n    - name: REGION\n      value: ap-northeast-2\n"
        )
    return dict(
        title="8. YAML config (30 services)",
        content="services:\n" + "".join(services),
        question="Which service is scaled to zero?",
        must_keep="service-19",
        tool_name="kubectl_get_config",
    )


if __name__ == "__main__":
    main(build)
