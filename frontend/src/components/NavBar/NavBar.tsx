import {
  AppBar as MUIAppBar,
  Container,
  Toolbar,
  Typography,
} from "@mui/material";

export const NavBar = () => {
  return (
    <MUIAppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Typography component="div" noWrap variant="h6">
            Swift Transaction Tracker
          </Typography>
        </Toolbar>
      </Container>
    </MUIAppBar>
  );
};
