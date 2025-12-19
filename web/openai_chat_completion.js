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
                         return app.graph.getNodeById(app.graph.getLink(clientInput.link)?.origin_id);
                     }
                     return null;
                }

                // Function to update model options
                const updateModelOptions = async () => {
                    modelWidget.options.values = [];
                    const linkedNode = getClientInputNode();
                    if (linkedNode) {
                        const apiKeyWidget = linkedNode.widgets.find(w => w.name === "api_key");
                        const baseUrlWidget = linkedNode.widgets.find(w => w.name === "base_url");
                        if (apiKeyWidget && apiKeyWidget.value) {
                            const baseUrl = baseUrlWidget?.value ?? "https://api.openai.com/v1";
                            try {
                                const response = await fetch('/sg_openai_models', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({
                                        api_key: apiKeyWidget.value,
                                        base_url: baseUrl
                                    })
                                });
                                if (response.ok) {
                                    const models = await response.json();
                                    modelWidget.options.values = models;
                                    if (!models.includes(modelWidget.value)) {
                                        modelWidget.value = models[0] ?? modelWidget.value;
                                    }
                                    node.setDirtyCanvas(true, true);
                                } else {
                                    console.error("Failed to fetch models:", response.status, response.statusText);
                                }
                            } catch (error) {
                                console.error("Error fetching models:", error);
                            }
                        }
                    }
                };

                // Function to setup listeners on linked node's widgets
                const setupListeners = () => {
                    const linkedNode = getClientInputNode();
                    if (linkedNode) {
                        const apiKeyWidget = linkedNode.widgets.find(w => w.name === "api_key");
                        const baseUrlWidget = linkedNode.widgets.find(w => w.name === "base_url");
                        if (apiKeyWidget) {
                            apiKeyWidget.callback = () => updateModelOptions();
                        }
                        if (baseUrlWidget) {
                            baseUrlWidget.callback = () => updateModelOptions();
                        }
                    }
                };

                node.onConnectionsChange = () => {
                    const currentClientLinkId = getClientInputNode()?.id;
                    if (currentClientLinkId !== previousClientLinkId) {
                        previousClientLinkId = currentClientLinkId;
                        //for whatever reason, this doesn't work if called in the same tick as the node is created'
                        setTimeout(() => {
                          updateModelOptions();
                          setupListeners();
                        })
                    }
                };
            }
        }
    }
});
