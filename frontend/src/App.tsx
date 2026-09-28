import {
    BrowserRouter,
    Navigate,
    Route,
    Routes,
} from "react-router-dom";

import Auth from "./pages/Auth";
import Research from "./pages/Research";

function App() {
    return (
        <BrowserRouter>
            <Routes>

                <Route
                    path="/auth"
                    element={<Auth />}
                />

                <Route
                    path="/research"
                    element={<Research />}
                />

                <Route
                    path="*"
                    element={
                        <Navigate
                            to="/auth"
                            replace
                        />
                    }
                />

            </Routes>
        </BrowserRouter>
    );
}

export default App;