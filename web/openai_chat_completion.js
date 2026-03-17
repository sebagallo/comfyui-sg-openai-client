import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "comfyui-sg-openai-client.OpenAIChatCompletion",
    async nodeCreated(node) {
        if (node.comfyClass === "OpenAIChatCompletion") {
            const modelWidget = node.widgets.find(w => w.name === "model");
            if (modelWidget) {
                let previousClientLinkId = null;

                const getClientInputNode = () => {
                    const clientInput = node.inputs.find(i => i.name === "client");
                    if (clientInput && clientInput.link) {
                        return node.graph.getNodeById(node.graph.getLink(clientInput.link)?.origin_id);
                    }
                    return null;
                }

                // Debounce function
                const debounce = (func, delay) => {
                    let timeoutId;
                    return (...args) => {
                        clearTimeout(timeoutId);
                        timeoutId = setTimeout(() => {
                            func.apply(null, args);
                        }, delay);
                    };
                };

                // Function to update model options
                const updateModelOptions = async () => {
                    const linkedNode = getClientInputNode();
                    if (!linkedNode) {
                        modelWidget.options.values = [];
                        node.setDirtyCanvas(true, true);
                        return;
                    }

                    const apiKeyWidget = linkedNode.widgets.find(w => w.name === "api_key");
                    const baseUrlWidget = linkedNode.widgets.find(w => w.name === "base_url");
                    const baseUrl = baseUrlWidget?.value ?? "https://api.openai.com/v1";
                    const originalValue = node.modelBeforeUpdate || modelWidget.value;

                    try {
                        const response = await fetch('/sg_openai_models', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                api_key: apiKeyWidget?.value,
                                base_url: baseUrl
                            })
                        });
                        if (response.ok) {
                            const models = await response.json();
                            modelWidget.options.values = models;
                            if (models.includes(originalValue)) {
                                modelWidget.value = originalValue;
                            } else {
                                modelWidget.value = models[0] ?? "";
                            }
                        } else {
                            console.error("Failed to fetch models:", response.status, response.statusText);
                            modelWidget.options.values = ["Error fetching models"];
                            modelWidget.value = "Error fetching models";
                        }
                    } catch (error) {
                        console.error("Error fetching models:", error);
                        modelWidget.options.values = ["Error fetching models"];
                        modelWidget.value = "Error fetching models";
                    }
                    node.modelBeforeUpdate = null;
                    node.setDirtyCanvas(true, true);
                };

                const debouncedUpdateModelOptions = debounce(updateModelOptions, 1000);

                const triggerUpdate = () => {
                    if (modelWidget.value !== "Loading...") {
                        node.modelBeforeUpdate = modelWidget.value;
                    }
                    modelWidget.options.values = ["Loading..."];
                    modelWidget.value = "Loading...";
                    node.setDirtyCanvas(true, true);
                    debouncedUpdateModelOptions();
                };

                triggerUpdate();

                // Function to setup listeners on linked node's widgets
                const setupListeners = () => {
                    const linkedNode = getClientInputNode();
                    if (linkedNode) {
                        const apiKeyWidget = linkedNode.widgets.find(w => w.name === "api_key");
                        const baseUrlWidget = linkedNode.widgets.find(w => w.name === "base_url");
                        if (apiKeyWidget) {
                            apiKeyWidget.callback = () => triggerUpdate();
                        }
                        if (baseUrlWidget) {
                            baseUrlWidget.callback = () => triggerUpdate();
                        }
                    }
                };

                node.onConnectionsChange = () => {
                    const currentClientLinkId = getClientInputNode()?.id;
                    if (currentClientLinkId !== previousClientLinkId) {
                        previousClientLinkId = currentClientLinkId;
                        //for whatever reason, this doesn't work if called in the same tick as the node is created'
                        setTimeout(() => {
                            triggerUpdate();
                            setupListeners();
                        })
                    }
                };
            }
        }
    }
});
